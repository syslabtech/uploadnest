# Frontend – React File Upload Client

A secure, production-ready React frontend for uploading, chunking, and managing files with a modern UI. Integrates with a FastAPI backend and GitLab for storage.

## Folder Structure

```
frontend/
│   Dockerfile
│   package.json
│   package-lock.json
│   .env.example
│   README.md
│   .gitignore
│   .dockerignore
│   .gitlab-ci.yml
│   .github/
│     workflows/ci.yml
│   nginx.conf
│
├── public/
├── src/
│   ├── App.js
│   ├── components/
│   └── ...
```

## Environment Variables
- Copy `.env.example` to `.env` and fill in your backend API URL and other values.
- **Never commit `.env` to version control.**
- Example:
  - `REACT_APP_BACKEND_URL=https://your-backend-url`

## Running in Production

### 1. Build & Run with Docker
```sh
cd frontend
# Build image
docker build -t fileupload-frontend .
# Run container (mount or provide .env at runtime)
docker run -d -p 8080:80 --name fileupload-frontend fileupload-frontend
```

### 2. Run Manually (Dev Only)
- Install Node.js 22+
- `npm ci --omit=dev`
- `npm start`

## CI/CD
- **GitHub Actions:** `.github/workflows/ci.yml` (build, test, Docker build)
- **GitLab CI:** `.gitlab-ci.yml` (build, test, deploy)

## Security & Best Practices
- No secrets in repo or Docker images
- Hardened nginx config, security headers, anti-cloning/scraping
- Modular code for maintainability
- All static and config files ignored via `.gitignore`/`.dockerignore`

---
For more, see the main project README or ask for deployment help!
