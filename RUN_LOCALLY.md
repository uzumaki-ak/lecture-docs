# 🚀 Running LectureDocs Locally - Complete Guide

This guide will walk you through running the entire system on your local machine.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Docker Desktop** (v20.10+) - [Download](https://www.docker.com/products/docker-desktop)
- [ ] **Docker Compose** (v2.0+) - Usually included with Docker Desktop
- [ ] **Python 3.11+** - [Download](https://www.python.org/downloads/)
- [ ] **Node.js 18+** - [Download](https://nodejs.org/)
- [ ] **Git** - [Download](https://git-scm.com/)
- [ ] **8GB RAM minimum** (16GB recommended)
- [ ] **20GB free disk space**
- [ ] (Optional) **NVIDIA GPU** for faster OCR/LLM processing

### Verify Installation

```bash
# Check Docker
docker --version
docker-compose --version

# Check Python
python --version  # or python3 --version

# Check Node.js
node --version
npm --version

# Check Git
git --version
```

---

## 🎯 Option 1: Quick Start with Docker Compose (Recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/lecture-docs.git
cd lecture-docs
```

### Step 2: Set Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Open .env in your editor
nano .env  # or use your preferred editor
```

**Minimum required for FREE tier:**

```bash
# Edit these lines in .env:
GEMINI_API_KEY=your_gemini_key_here  # Get from: https://aistudio.google.com/app/apikey
EURON_API_KEY=your_euron_key_here    # Get from: https://www.euron.one/api-keys

# Keep these as-is:
MODE=local
DEV_AUTH=true
LLM_PROVIDER=gemini
```

### Step 3: Start All Services

```bash
# Build and start all containers
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

This starts:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis cache (port 6379)
- ✅ Chroma vector DB (port 8000)
- ✅ Backend API (port 8080)
- ✅ Frontend UI (port 3000)
- ✅ Background worker

### Step 4: Run Database Migrations

```bash
# Wait 10 seconds for containers to fully start
sleep 10

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Step 5: Access the Application

Open your browser:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs (interactive Swagger)
- **Health Check**: http://localhost:8080/api/health

### Step 6: Test the System

1. Go to http://localhost:3000
2. Click "New Project"
3. Upload a test image (handwritten notes or typed text)
4. Wait for processing (check logs: `docker-compose logs -f worker`)
5. View generated documentation
6. Try the chatbot!

### Stopping the System

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

---

## 🛠️ Option 2: Manual Setup (For Development)

For active development, you might want to run components separately.

### Step 1: Clone & Setup

```bash
git clone https://github.com/yourusername/lecture-docs.git
cd lecture-docs
cp .env.example .env
# Edit .env with your API keys
```

### Step 2: Start Infrastructure Services

```bash
# Start only DB, Redis, and Chroma
docker-compose up -d postgres redis chroma

# Verify they're running
docker-compose ps
```

### Step 3: Set Up Python Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download required models (first time only)
python -c "from transformers import pipeline; pipeline('image-to-text', model='microsoft/trocr-base-handwritten')"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Run migrations
alembic upgrade head

# Start the backend
uvicorn app.main:app --reload --port 8080
```

**Backend should now be running at http://localhost:8080**

### Step 4: Start Background Worker

Open a new terminal:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the worker
python -m app.services.job_queue
```

### Step 5: Set Up Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend should now be running at http://localhost:3000**

---

## 📥 Downloading Local Models (Optional but Recommended)

For fully offline operation with local LLMs:

### Option A: Using Ollama (Easiest)

```bash
# Install Ollama
# macOS:
brew install ollama

# Linux:
curl https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/

# Pull models
ollama pull llama3.2:3b
ollama pull llama3.2:1b  # Smaller, faster

# Start Ollama server
ollama serve

# Update .env
echo "LOCAL_LLM_URL=http://localhost:11434" >> .env
echo "USE_LOCAL_LLM=true" >> .env
```

### Option B: Using llama.cpp

```bash
cd backend/models

# Download model (example: Llama 3.2 3B)
wget https://huggingface.co/QuantFactory/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct.Q4_K_M.gguf

# Install llama-cpp-python
pip install llama-cpp-python

# Update .env
echo "LOCAL_LLM_PATH=/app/models/Llama-3.2-3B-Instruct.Q4_K_M.gguf" >> .env
```

---

## 🔑 Getting API Keys (Free Tier)

### 1. Gemini API Key (FREE - Recommended)

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Add to `.env`: `GEMINI_API_KEY=your_key_here`

**Limits**: 
- 1,500 requests per day (free tier)
- 1 million tokens per minute
- Models: gemini-2.0-flash-exp (free), gemini-1.5-pro (free)

### 2. Euron.one API Key (FREE)

1. Go to https://www.euron.one/
2. Sign up for free account
3. Go to API Keys section
4. Create new API key
5. Add to `.env`: `EURON_API_KEY=your_key_here`

**Limits**: 
- Multiple free models available
- Rate limits apply (check dashboard)

### 3. Clerk Auth (Optional - FREE tier)

1. Go to https://clerk.com/
2. Create account & new application
3. Get publishable key & secret key
4. Add to `.env`:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
DEV_AUTH=false
```

---

## 🧪 Testing the Installation

### Health Check

```bash
# Backend health
curl http://localhost:8080/api/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "chroma": "connected",
  "timestamp": "2025-01-19T..."
}
```

### Upload a Test File

```bash
# Create a test text file
echo "# Blockchain Basics

Smart contracts are self-executing contracts with the terms directly written into code." > test-notes.txt

# Upload via API
curl -X POST http://localhost:8080/api/upload \
  -F "file=@test-notes.txt" \
  -F "project_name=test-project" \
  -F "course=blockchain-101" \
  -F "module=mod-1" \
  -F "lecture=lec-1"

# Check the job status
curl http://localhost:8080/api/jobs/{job_id}
```

### Test OCR with Handwritten Notes

1. Take a photo of your handwritten notes
2. Go to http://localhost:3000
3. Upload the image
4. Wait for OCR processing
5. View the extracted text and generated documentation

---

## 🐛 Troubleshooting

### Issue: "Connection refused" errors

**Solution**: Make sure all services are running
```bash
docker-compose ps
# All services should show "Up" status
```

### Issue: "Out of memory" when processing large files

**Solution**: Increase Docker memory limit
1. Docker Desktop → Settings → Resources
2. Increase memory to 8GB+
3. Restart Docker

### Issue: OCR is very slow

**Solutions**:
1. Use GPU acceleration (if available):
```bash
# Edit .env
USE_GPU=true
```

2. Use faster model:
```bash
# Edit .env
OCR_PROVIDER=tesseract  # Faster than TrOCR
```

3. Process smaller images:
   - Resize images to max 2000px width before upload

### Issue: Worker not processing jobs

**Solution**: Check worker logs
```bash
docker-compose logs -f worker

# Manually restart worker
docker-compose restart worker
```

### Issue: Database migration fails

**Solution**: Reset database
```bash
# Stop services
docker-compose down -v

# Remove volumes
docker volume rm lecture-docs_postgres_data

# Restart and migrate
docker-compose up -d
sleep 10
docker-compose exec backend alembic upgrade head
```

### Issue: Frontend can't connect to backend

**Solution**: Check CORS and API URL
```bash
# In frontend/.env
NEXT_PUBLIC_API_URL=http://localhost:8080

# In backend/.env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 📊 Monitoring & Logs

### View All Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend
```

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d lecture_docs

# List tables
\dt

# Query projects
SELECT id, name, slug, created_at FROM projects;
```

### Access Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check keys
KEYS *

# Monitor commands
MONITOR
```

---

## 🚀 Performance Optimization

### 1. Use SSD for Storage

Mount volumes on SSD for faster I/O:
```yaml
# docker-compose.yml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      device: /path/to/ssd/postgres
      o: bind
```

### 2. Enable Redis Persistence

```bash
# Edit docker-compose.yml
redis:
  command: redis-server --appendonly yes --save 60 1000
```

### 3. Pre-download Models

```bash
# Download all models before first use
cd backend
python scripts/download_models.py
```

### 4. Use Production WSGI Server

For production deployment:
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
```

---

## 🎓 Next Steps

1. **Customize**: Edit prompts in `backend/app/prompts/readme_prompt.py`
2. **Add Models**: Download more OCR/LLM models
3. **Scale**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for scaling guide
4. **Integrate**: Connect to your note-taking workflow
5. **Extend**: Build custom parsers in `backend/app/services/parser_service.py`

---

## 📞 Need Help?

- 📖 **Documentation**: Check [README.md](./README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/uzumaki-ak/lecture-docs/issues)
- 💬 **Discord**: Join our community
- 📧 **Email**: anikeshuzumaki@gmail.com-

Happy learning! 🎉