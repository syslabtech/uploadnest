# Backend – FastAPI File Upload System

A secure, production-ready backend for chunked file uploads, GitLab integration, and PostgreSQL metadata storage. Modular, CI/CD-ready, and built for modern deployments.

## Folder Structure

```
backend/
│   Dockerfile
│   requirements.txt
│   .env.example
│   README.md
│   .gitignore
│   .dockerignore
│   .gitlab-ci.yml
│   .github/
│     workflows/ci.yml
│
├── main.py           # Entrypoint: from app.main import app
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI app, security headers
│   ├── auth.py       # Authentication logic
│   ├── database.py   # DB connection (asyncpg)
│   ├── routes.py     # API routes
│   ├── models.py     # (Optional) SQLAlchemy models
│   ├── schemas/      # Pydantic schemas (split by domain)
│   └── utils/        # Utility functions
```

## Environment Variables
- Copy `.env.example` to `.env` and fill in your production values.
- **Never commit `.env` to version control.**
- Required variables:
  - `POSTGRES_URL` (PostgreSQL connection string)
  - `GITLAB_TOKEN`, `GITLAB_GROUP_ID`, `GITLAB_URL`
  - `ALLOWED_ORIGINS` (comma-separated CORS origins)
  - `BASIC_AUTH_USERNAME`, `PASSWORD_HASH` (MD5 hash)

## Running in Production

### 1. Build & Run with Docker
```sh
cd backend
# Build image
docker build -t fileupload-backend .
# Run container (mount or provide .env at runtime)
docker run -d --env-file .env -p 8001:8001 --name fileupload-backend fileupload-backend
```

### 2. Run Manually (Dev Only)
- Install Python 3.12+
- `pip install -r requirements.txt`
- `uvicorn main:app --host 0.0.0.0 --port 8001`

## CI/CD
- **GitHub Actions:** `.github/workflows/ci.yml` (build, test, Docker build)
- **GitLab CI:** `.gitlab-ci.yml` (build, test, deploy)

## Security & Best Practices
- No secrets in repo or Docker images
- Hardened CORS, security headers, anti-cloning/scraping
- Modular code for maintainability
- All static and config files ignored via `.gitignore`/`.dockerignore`

---
For more, see the main project README or ask for deployment help!
