# Deployment Guide

This guide covers deploying the AI-Powered Todo Chatbot with:
- **Frontend**: Vercel (Next.js)
- **Backend**: Render (FastAPI)
- **Database**: Neon PostgreSQL (already configured)

## Architecture Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Vercel (Frontend) │────▶│   Render (Backend)  │────▶│  Neon PostgreSQL    │
│   Next.js App       │     │   FastAPI Server    │     │  Database           │
│   todo-chatbot.     │     │   api.render.com    │     │  neon.tech          │
│   vercel.app        │     │                     │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

---

## Prerequisites

Before deploying, ensure you have:

1. **GitHub Repository**: Code pushed to GitHub
2. **Neon Account**: Database already set up at [neon.tech](https://neon.tech)
3. **OpenAI API Key**: From [platform.openai.com](https://platform.openai.com/api-keys)
4. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
5. **Render Account**: Sign up at [render.com](https://render.com)

---

## Part 1: Deploy Backend on Render

### Step 1: Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository: `AI-Todo-Chatbot`

### Step 2: Configure the Service

| Setting | Value |
|---------|-------|
| **Name** | `ai-todo-chatbot-api` |
| **Region** | Choose closest to your users |
| **Branch** | `main` or `001-mcp-todo-chatbot` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free (or paid for production) |

### Step 3: Add Environment Variables

In the Render dashboard, go to **Environment** and add:

| Key | Value | Description |
|-----|-------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Your Neon connection string |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key |
| `ENVIRONMENT` | `production` | Environment mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PYTHON_VERSION` | `3.11.0` | Python version |

> **Important**: Get your `DATABASE_URL` from Neon Console. Make sure it starts with `postgresql+asyncpg://`

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for the build and deployment (5-10 minutes)
3. Once deployed, note your backend URL: `https://ai-todo-chatbot-api.onrender.com`

### Step 5: Verify Backend Deployment

Test the health endpoint:
```bash
curl https://ai-todo-chatbot-api.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "service": "ai-todo-chatbot"}
```

---

## Part 2: Deploy Frontend on Vercel

### Step 1: Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository: `AI-Todo-Chatbot`

### Step 2: Configure Project

| Setting | Value |
|---------|-------|
| **Project Name** | `ai-todo-chatbot` |
| **Framework Preset** | `Next.js` (auto-detected) |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` (default) |
| **Output Directory** | `.next` (default) |
| **Install Command** | `npm install` (default) |

### Step 3: Add Environment Variables

Click **"Environment Variables"** and add:

| Key | Value | Environment |
|-----|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://ai-todo-chatbot-api.onrender.com` | Production |

> **Important**: Replace with your actual Render backend URL from Part 1

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for the build (2-3 minutes)
3. Once deployed, note your frontend URL: `https://ai-todo-chatbot.vercel.app`

### Step 5: Verify Frontend Deployment

1. Open your Vercel URL in a browser
2. You should see the AI Todo Chatbot interface
3. Try sending a message: "Add a task to test deployment"

---

## Part 3: Post-Deployment Configuration

### Update CORS (if needed)

If you encounter CORS errors, update `backend/src/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-todo-chatbot.vercel.app",  # Your Vercel URL
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend on Render.

### Custom Domain (Optional)

**Vercel (Frontend):**
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

**Render (Backend):**
1. Go to Service Settings → Custom Domains
2. Add your API subdomain (e.g., `api.yourdomain.com`)
3. Follow DNS configuration instructions

---

## Environment Variables Reference

### Backend (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `ENVIRONMENT` | No | `development`, `staging`, `production` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `PYTHON_VERSION` | No | Python version for Render |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |

---

## Troubleshooting

### Backend Issues

**Build Fails:**
- Check `requirements.txt` exists in `backend/` directory
- Verify Python version compatibility (3.11+)

**Database Connection Error:**
- Verify `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host/db?ssl=require`
- Check Neon database is active and accessible

**OpenAI API Error:**
- Verify `OPENAI_API_KEY` is valid and has credits
- Check API key has correct permissions

### Frontend Issues

**API Connection Error:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running and healthy
- Check CORS configuration

**Build Error:**
- Run `npm run build` locally to check for errors
- Verify all dependencies are in `package.json`

### Common Fixes

**Render Cold Starts (Free Tier):**
- Free tier instances spin down after inactivity
- First request may take 30-60 seconds
- Consider paid tier for production

**Vercel Timeout:**
- Default timeout is 10 seconds
- Increase timeout in `vercel.json` if needed

---

## Deployment Checklist

### Before Deploying

- [ ] Code pushed to GitHub
- [ ] Neon database created and connection string ready
- [ ] OpenAI API key ready
- [ ] Tested locally and working

### Backend (Render)

- [ ] Web service created
- [ ] Root directory set to `backend`
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables added
- [ ] Health endpoint returns `{"status": "healthy"}`

### Frontend (Vercel)

- [ ] Project imported from GitHub
- [ ] Root directory set to `frontend`
- [ ] `NEXT_PUBLIC_API_URL` environment variable set
- [ ] Build succeeds
- [ ] Chat interface loads
- [ ] Can send messages and receive responses

### Post-Deployment

- [ ] CORS configured (if needed)
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up (optional)

---

## Monitoring and Logs

### Render Logs

1. Go to Render Dashboard → Your Service
2. Click **"Logs"** tab
3. View real-time logs

### Vercel Logs

1. Go to Vercel Dashboard → Your Project
2. Click **"Deployments"** → Select deployment
3. Click **"Functions"** tab for serverless logs

---

## Cost Estimates

### Free Tier

| Service | Tier | Limitations |
|---------|------|-------------|
| Vercel | Hobby | 100GB bandwidth/month |
| Render | Free | Spins down after 15 min inactivity |
| Neon | Free | 3GB storage, 1 compute |
| OpenAI | Pay-as-you-go | ~$0.01 per conversation |

### Production (Estimated)

| Service | Tier | Cost |
|---------|------|------|
| Vercel | Pro | $20/month |
| Render | Starter | $7/month |
| Neon | Launch | $19/month |
| OpenAI | - | Usage-based |

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review deployment logs on Render/Vercel
3. Open an issue on GitHub

---

**Happy Deploying!**
