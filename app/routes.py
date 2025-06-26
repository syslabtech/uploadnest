from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from app.schemas.file import FileMetadata, FileMetadataResponse, ChunkMetadata
from app.schemas.repo import RepositoryResponse
from app.database import save_file_metadata, save_chunk_metadata, get_all_file_metadata
from app.auth import basic_auth
import os
from pathlib import Path
from dotenv import load_dotenv
import gitlab
from gitlab.exceptions import GitlabCreateError, GitlabGetError
import base64
import asyncpg
from datetime import datetime
import tempfile
import logging

# Always load .env from backend root
BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / '.env')

router = APIRouter(prefix="/api")

# GitLab setup
GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
GROUP_ID = int(os.environ.get("GITLAB_GROUP_ID", "109704268"))
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "5242880"))

TEMP_DIR = Path(tempfile.gettempdir()) / "gitlab_chunks"
TEMP_DIR.mkdir(exist_ok=True)

gl = gitlab.Gitlab(url=GITLAB_URL, private_token=GITLAB_TOKEN)

logger = logging.getLogger(__name__)

@router.get("/")
async def root(auth: bool = Depends(basic_auth)):
    return {"message": "File Upload System API", "version": "1.0.0"}

@router.post("/gitlab/create-repository")
async def create_repository(repo_name: str = Form(...), auth: bool = Depends(basic_auth)):
    try:
        group = gl.groups.get(GROUP_ID)
        project_data = {
            'name': repo_name,
            'namespace_id': GROUP_ID,
            'visibility': 'private',
            'initialize_with_readme': True
        }
        project = gl.projects.create(project_data)
        return {
            "success": True,
            "project_id": project.id,
            "project_name": project.name,
            "repo_url": project.web_url,
            "clone_url": project.http_url_to_repo
        }
    except GitlabCreateError as e:
        raise HTTPException(status_code=400, detail=f"Failed to create repository: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/gitlab/upload-chunk/{project_id}")
async def upload_chunk(
    project_id: int,
    file: UploadFile = File(...),
    chunk_number: int = Form(...),
    total_chunks: int = Form(...),
    file_name: str = Form(...),
    upload_id: str = Form(...),
    auth: bool = Depends(basic_auth)
):
    try:
        logger.info(f"Uploading chunk {chunk_number + 1}/{total_chunks} for file {file_name}")
        upload_dir = TEMP_DIR / upload_id
        upload_dir.mkdir(exist_ok=True)
        chunk_path = upload_dir / f"{file_name}.part{chunk_number:04d}"
        content = await file.read()
        with open(chunk_path, "wb") as buffer:
            buffer.write(content)
        logger.info(f"Chunk {chunk_number + 1} saved: {len(content)} bytes")
        project = gl.projects.get(project_id)
        chunk_gitlab_path = f"{file_name}.part{chunk_number:04d}"
        chunk_content_b64 = base64.b64encode(content).decode('utf-8')
        file_exists = False
        existing_file = None  # Fix for possibly unbound variable
        try:
            existing_file = project.files.get(file_path=chunk_gitlab_path, ref='main')
            file_exists = True
            logger.info(f"Chunk file {chunk_gitlab_path} already exists, updating...")
        except GitlabGetError:
            logger.info(f"Chunk file {chunk_gitlab_path} doesn't exist, creating new...")
        if file_exists and existing_file is not None:
            existing_file.content = chunk_content_b64
            existing_file.save(branch='main', commit_message=f"Update chunk {chunk_gitlab_path}")
        else:
            project.files.create({
                'file_path': chunk_gitlab_path,
                'branch': 'main',
                'content': chunk_content_b64,
                'commit_message': f"Add chunk {chunk_gitlab_path}",
                'encoding': 'base64'
            })
        logger.info(f"Chunk {chunk_number + 1} uploaded to GitLab as {chunk_gitlab_path}")
        chunk_metadata = ChunkMetadata(
            upload_id=upload_id,
            original_filename=file_name,
            chunk_number=chunk_number,
            chunk_size=len(content),
            gitlab_repo_id=project_id,
            gitlab_repo_name=project.name,
            gitlab_chunk_path=chunk_gitlab_path,
            content_type=file.content_type if hasattr(file, 'content_type') else 'application/octet-stream'
        )
        await save_chunk_metadata(chunk_metadata)
        logger.info(f"Chunk metadata saved for chunk {chunk_number + 1}")
        if chunk_number + 1 == total_chunks:
            file_size = 0
            try:
                conn = await asyncpg.connect(os.environ['POSTGRES_URL'])
                row = await conn.fetchrow('SELECT SUM(chunk_size) as total_size FROM chunk_metadata WHERE upload_id=$1', upload_id)
                await conn.close()
                if row and row['total_size']:
                    file_size = row['total_size']
            except Exception as e:
                logger.error(f"Error calculating file size from chunk_metadata: {e}")
            if not file_size:
                file_size = len(content) * total_chunks
            file_metadata = FileMetadata(
                original_filename=file_name,
                file_size=file_size,
                chunk_count=total_chunks,
                gitlab_repo_id=project_id,
                gitlab_repo_name=project.name,
                gitlab_file_path=file_name,
                content_type=file.content_type if hasattr(file, 'content_type') else 'application/octet-stream'
            )
            await save_file_metadata(file_metadata)
            logger.info(f"File metadata saved for {file_name}")
        if chunk_path.exists():
            chunk_path.unlink()
        response_data = {
            "success": True,
            "message": f"Chunk {chunk_number + 1}/{total_chunks} uploaded to GitLab",
            "chunk_number": chunk_number,
            "total_chunks": total_chunks,
            "gitlab_chunk_path": chunk_gitlab_path,
            "completed": chunk_number + 1 == total_chunks
        }
        if chunk_number + 1 == total_chunks:
            try:
                conn = await asyncpg.connect(os.environ['POSTGRES_URL'])
                row = await conn.fetchrow('SELECT id FROM file_metadata WHERE original_filename=$1 ORDER BY upload_timestamp DESC LIMIT 1', file_name)
                await conn.close()
                if row:
                    response_data["postgres_doc_id"] = row["id"]
                else:
                    response_data["postgres_doc_id"] = None
            except Exception as e:
                response_data["postgres_doc_id"] = None
        return JSONResponse(content=response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_chunk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@router.get("/gitlab/repositories")
async def list_repositories(auth: bool = Depends(basic_auth)):
    try:
        group = gl.groups.get(GROUP_ID)
        projects = group.projects.list(all=True)
        return {
            "success": True,
            "repositories": [
                {
                    "id": project.id,
                    "name": project.name,
                    "url": project.web_url,
                    "created_at": project.created_at
                }
                for project in projects
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing repositories: {str(e)}")

@router.get("/files", response_model=list[FileMetadataResponse])
async def get_uploaded_files(auth: bool = Depends(basic_auth)):
    try:
        files = await get_all_file_metadata()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {str(e)}")
