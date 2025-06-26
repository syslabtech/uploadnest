from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class FileMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_filename: str
    file_size: int
    chunk_count: int
    gitlab_repo_id: int
    gitlab_repo_name: str
    gitlab_file_path: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"
    content_type: Optional[str] = None

class FileMetadataResponse(BaseModel):
    id: str
    original_filename: str
    file_size: int
    chunk_count: int
    gitlab_repo_id: int
    gitlab_repo_name: str
    gitlab_file_path: str
    upload_timestamp: datetime
    status: str
    content_type: Optional[str] = None

class ChunkMetadata(BaseModel):
    upload_id: str
    original_filename: str
    chunk_number: int
    chunk_size: int
    gitlab_repo_id: int
    gitlab_repo_name: str
    gitlab_chunk_path: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"
    content_type: Optional[str] = None
