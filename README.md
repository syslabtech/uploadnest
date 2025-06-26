# Backend - FastAPI File Upload System

## Folder Structure

```
backend/
│   Dockerfile
│   requirements.txt
│   .env.example
│   README.md
│
├── app/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── schemas/
│   └── __init__.py
├── main.py         # FastAPI entrypoint
├── auth.py         # Authentication logic
├── database.py     # DB connection
├── models.py       # SQLAlchemy models
├── routes.py       # API routes
└── ...
```

## Running in Production

### 1. Environment Variables
- Copy `.env.example` to `.env` and fill in your production values.
- Required variables:
  - `POSTGRES_URL` (PostgreSQL connection string)
  - `GITLAB_TOKEN`, `GITLAB_GROUP_ID`, `GITLAB_URL`
  - `ALLOWED_ORIGINS` (comma-separated CORS origins)
  - `AUTH_USERNAME`, `AUTH_PASSWORD_HASH` (MD5 hash)

### 2. Build & Run with Docker

```
# From project root
cd backend
# Build image
docker build -t fileupload-backend .
# Run container (edit env file path as needed)
docker run -d --env-file .env -p 8001:8001 --name fileupload-backend fileupload-backend
```

### 3. Run Manually (Not Recommended for Production)
- Install Python 3.12+
- `pip install -r requirements.txt`
- `uvicorn main:app --host 0.0.0.0 --port 8001`

### 4. Default Settings
- If `.env` is missing, the app will not start. Always provide a valid `.env`.
- CORS, DB, and GitLab settings must be set for production.

---

For more details, see the main project README.
