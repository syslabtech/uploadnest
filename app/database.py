import os
import asyncpg
from pathlib import Path
from dotenv import load_dotenv
import logging

# Always load .env from backend root
BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / '.env')

postgres_url = os.environ['POSTGRES_URL']

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("db_connectivity")

async def init_database():
    try:
        logger.debug("Attempting to connect to the database...")
        conn = await asyncpg.connect(postgres_url)
        logger.info("Database connection established.")
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
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

async def save_file_metadata(metadata):
    try:
        logger.debug("Connecting to database for saving file metadata...")
        conn = await asyncpg.connect(postgres_url)
        logger.debug(f"Connected. Saving file metadata: {metadata}")
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
        logger.info("File metadata saved successfully.")
    except Exception as e:
        logger.error(f"Error saving file metadata: {e}")
    finally:
        await conn.close()

async def save_chunk_metadata(metadata):
    try:
        logger.debug("Connecting to database for saving chunk metadata...")
        conn = await asyncpg.connect(postgres_url)
        logger.debug(f"Connected. Inserting chunk metadata: {metadata}")
        await conn.execute('''
            INSERT INTO chunk_metadata 
            (upload_id, original_filename, chunk_number, chunk_size, gitlab_repo_id, 
             gitlab_repo_name, gitlab_chunk_path, upload_timestamp, status, content_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', 
        metadata.upload_id, metadata.original_filename, metadata.chunk_number, metadata.chunk_size,
        metadata.gitlab_repo_id, metadata.gitlab_repo_name, metadata.gitlab_chunk_path,
        metadata.upload_timestamp, metadata.status, metadata.content_type)
        logger.info(f"Chunk metadata insert successful for chunk_number={metadata.chunk_number}")
    except Exception as e:
        logger.error(f"Failed to insert chunk metadata: {e}")
    finally:
        await conn.close()

async def get_all_file_metadata():
    try:
        logger.debug("Connecting to database for fetching all file metadata...")
        conn = await asyncpg.connect(postgres_url)
        logger.debug("Connected. Fetching file metadata...")
        rows = await conn.fetch('SELECT * FROM file_metadata ORDER BY upload_timestamp DESC')
        logger.info(f"Fetched {len(rows)} file metadata records.")
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching file metadata: {e}")
        return []
    finally:
        await conn.close()
