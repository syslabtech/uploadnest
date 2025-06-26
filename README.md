# UploadNest – Monorepo Overview

A secure, scalable platform for chunked file uploads, GitLab repository storage, and PostgreSQL metadata, with a modern React frontend and FastAPI backend. This root README is for the **prod** branch, which coordinates both frontend and backend deployments for **UploadNest**.

---

## Repository Structure

- **prod branch**: Monorepo overview, deployment, and documentation (this file)
- **backend branch**: FastAPI backend (see `backend/README.md` for details)
- **frontend branch**: React frontend (see `frontend/README.md` for details)

---

## How to Use

### 1. Clone the Repository
```sh
git clone <repo-url>
cd uploadnest
```

### 2. Switch to the Desired Branch
- For backend: `git checkout backend`
- For frontend: `git checkout frontend`
- For production/deployment: `git checkout prod`

### 3. Backend Setup (FastAPI)
See `backend/README.md` for full details.
- Copy `.env.example` to `.env` and fill in secrets.
- Build and run with Docker:
  ```sh
  cd backend
  docker build -t uploadnest-backend .
  docker run -d --env-file .env -p 8001:8001 --name uploadnest-backend uploadnest-backend
  ```
- Or run locally for development:
  ```sh
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8001
  ```

### 4. Frontend Setup (React)
See `frontend/README.md` for full details.
- Copy `.env.example` to `.env` and set your backend API URL.
- Build and run with Docker:
  ```sh
  cd frontend
  docker build -t uploadnest-frontend .
  docker run -d -p 8080:80 --name uploadnest-frontend uploadnest-frontend
  ```
- Or run locally for development:
  ```sh
  npm ci --omit=dev
  npm start
  ```

---

## Production Deployment
- Deploy both backend and frontend Docker images to your server or cloud provider.
- Use a reverse proxy (nginx, Caddy, etc.) to route traffic to frontend (port 80/8080) and backend (port 8001).
- Ensure `.env` files are provided at runtime and never committed to the repo.

---

## CI/CD
- Both frontend and backend have GitHub Actions and GitLab CI workflows for build, test, and Docker image creation.
- Customize deploy steps in `.github/workflows/ci.yml` and `.gitlab-ci.yml` as needed.

---

## Security & Best Practices
- No secrets in version control or Docker images.
- Hardened CORS, security headers, anti-cloning/scraping in both frontend and backend.
- Modular, maintainable code in both projects.

---

## More Information
- See `backend/README.md` and `frontend/README.md` in their respective branches for full API, environment, and developer documentation.
- For help or deployment support, contact the project maintainer.