# DemandWise — Production Deployment Guide

DemandWise is engineered as a unified full-stack platform featuring a **React 18 TypeScript frontend** and a high-performance **FastAPI (Python 3.12) backend**.

You can deploy the platform in **three different ways**, depending on your infrastructure preference:

---

## 🚀 Option 1: Unified Docker Deployment (Recommended)

This is the easiest and most robust method. A single Docker container builds both the frontend and backend, serving the entire application from port `8000`.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed.

### Deploy with Docker Compose
From the project root:

```bash
docker compose up --build -d
```

That's it!
- **Interactive Web Dashboard:** `http://localhost:8000`
- **Swagger REST API Documentation:** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/health`

### Deploy with Plain Docker CLI
```bash
# 1. Build the multi-stage image
docker build -t demandwise-platform .

# 2. Run container
docker run -d -p 8000:8000 \
  -e SERVE_FRONTEND=true \
  -e PORT=8000 \
  -e DEBUG=false \
  --name demandwise \
  demandwise-platform
```

---

## ☁️ Option 2: Free / Low-Cost PaaS (Render, Railway, Fly.io)

### A. Deploy on Render (Easiest Cloud Deploy)
1. Push your repository to **GitHub** or **GitLab**.
2. Go to [dashboard.render.com](https://dashboard.render.com/).
3. Click **New +** → **Web Service**.
4. Connect your repository.
5. Select **Docker** environment:
   - **Dockerfile Path:** `./Dockerfile`
   - **Plan:** Free
6. Add Environment Variables:
   - `SERVE_FRONTEND` = `true`
   - `DEBUG` = `false`
   - `PORT` = `8000`
7. Click **Create Web Service**. Render will automatically build the React frontend and launch Uvicorn. Your live URL will be ready at `https://<your-subdomain>.onrender.com`.

*(Alternatively, use `render.yaml` via **New +** → **Blueprint**)*

---

### B. Deploy on Railway
1. Go to [railway.app](https://railway.app/).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Railway automatically detects the `Dockerfile`.
4. Set Environment Variables:
   - `SERVE_FRONTEND` = `true`
   - `PORT` = `8000`
5. Generate a domain under **Settings** → **Networking**.

---

### C. Deploy on Google Cloud Run / AWS App Runner
Because DemandWise includes a standard multi-stage `Dockerfile`:
```bash
# Google Cloud Run
gcloud run deploy demandwise \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SERVE_FRONTEND=true,DEBUG=false
```

---

## 🌐 Option 3: Split Deployment (Vercel + Render)

If you prefer hosting the React frontend on **Vercel** / **Netlify** and the FastAPI backend on **Render** / **Railway**:

### 1. Deploy Backend (FastAPI on Render/Railway)
- Root Directory: `.`
- Build Command: `pip install -r requirements.txt && pip install -e . --no-deps`
- Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Env Vars:
  - `CORS_ORIGINS` = `https://<your-vercel-frontend>.vercel.app`
  - `DEBUG` = `false`

### 2. Deploy Frontend (React on Vercel)
- Root Directory: `frontend`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variables:
  - `VITE_API_URL` = `https://<your-backend-service>.onrender.com/api/v1`

---

## 🔒 Security & Production Checklist

- [x] **CORS:** Configured via `CORS_ORIGINS` environment variable.
- [x] **Health Check:** `/health` endpoint configured for container orchestrators.
- [x] **Audit Ledger:** SQLite database persistence mounted to `/app/artifacts`.
- [x] **Static Assets:** Gzip-compressed bundle and optimized cache headers.
