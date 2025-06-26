import os
import asyncpg
from pathlib import Path
from dotenv import load_dotenv

# Always load .env from backend root
BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / '.env')

postgres_url = os.environ['POSTGRES_URL']

async def init_database():
    try:
        conn = await asyncpg.connect(postgres_url)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS file_metadata (
                id VARCHAR(255) PRIMARY KEY,
                original_filename VARCHAR(500) NOT NULL,
                file_size BIGINT NOT NULL,
                chunk_count INTEGER NOT NULL,
                gitlab_repo_id INTEGER NOT NULL,
                gitlab_repo_name VARCHAR(500) NOT NULL,
                gitlab_file_path VARCHAR(1000) NOT NULL,
                upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'completed',
                content_type VARCHAR(200)
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS chunk_metadata (
                id SERIAL PRIMARY KEY,
                upload_id VARCHAR(255) NOT NULL,
                original_filename VARCHAR(500) NOT NULL,
                chunk_number INTEGER NOT NULL,
                chunk_size BIGINT NOT NULL,
                gitlab_repo_id INTEGER NOT NULL,
                gitlab_repo_name VARCHAR(500) NOT NULL,
                gitlab_chunk_path VARCHAR(1000) NOT NULL,
                upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'completed',
                content_type VARCHAR(200)
            )
        ''')
        await conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

async def save_file_metadata(metadata):
    conn = await asyncpg.connect(postgres_url)
    try:
        await conn.execute('''
            INSERT INTO file_metadata 
            (id, original_filename, file_size, chunk_count, gitlab_repo_id, 
             gitlab_repo_name, gitlab_file_path, upload_timestamp, status, content_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', 
        metadata.id, metadata.original_filename, metadata.file_size, 
        metadata.chunk_count, metadata.gitlab_repo_id, metadata.gitlab_repo_name,
        metadata.gitlab_file_path, metadata.upload_timestamp, metadata.status,
        metadata.content_type)
    finally:
        await conn.close()

async def save_chunk_metadata(metadata):
    conn = await asyncpg.connect(postgres_url)
    try:
        print(f"[DEBUG] Inserting chunk metadata: {metadata}")
        await conn.execute('''
            INSERT INTO chunk_metadata 
            (upload_id, original_filename, chunk_number, chunk_size, gitlab_repo_id, 
             gitlab_repo_name, gitlab_chunk_path, upload_timestamp, status, content_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', 
        metadata.upload_id, metadata.original_filename, metadata.chunk_number, metadata.chunk_size,
        metadata.gitlab_repo_id, metadata.gitlab_repo_name, metadata.gitlab_chunk_path,
        metadata.upload_timestamp, metadata.status, metadata.content_type)
        print(f"[DEBUG] Chunk metadata insert successful for chunk_number={metadata.chunk_number}")
    except Exception as e:
        print(f"[ERROR] Failed to insert chunk metadata: {e}")
    finally:
        await conn.close()

async def get_all_file_metadata():
    conn = await asyncpg.connect(postgres_url)
    try:
        rows = await conn.fetch('SELECT * FROM file_metadata ORDER BY upload_timestamp DESC')
        return [dict(row) for row in rows]
    finally:
        await conn.close()
