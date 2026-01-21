# 📚 LectureDocs - AI-Powered Learning Documentation System

Transform your handwritten lecture notes, PDFs, audio, and code into beautiful, kid-friendly documentation with AI-powered insights and per-project chatbots.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Node](https://img.shields.io/badge/node-18%2B-green)

## 🎯 Features

### Core Capabilities
- 📝 **Multi-Input Support**: Handwritten notes, PDFs, audio, video, code, YouTube links
- 🤖 **AI-Powered OCR**: TrOCR for handwritten text + Tesseract fallback
- 🎤 **Speech-to-Text**: Local Whisper + cloud fallbacks
- 📊 **Smart Documentation**: Auto-generates structured docs with examples
- 💬 **RAG Chatbot**: Per-project AI assistant with context
- 🔍 **Vector Search**: Semantic search across all your notes
- 📁 **Smart Organization**: Course/Module/Lecture folder structure
- 🌍 **Offline-First**: Works completely offline with local models
- 🎨 **Beautiful UI**: Dark/Light mode, vintage aesthetic

### AI & LLM Features
- **Multi-LLM Orchestration**: Gemini 2.5 Flash (free), Euron.one (free), OpenAI, Anthropic, Local models
- **Automatic Fallbacks**: If one provider fails, automatically tries next
- **Multiple API Keys**: Load balance across multiple keys per provider
- **Privacy Mode**: Force all processing to stay local
- **Embeddings**: sentence-transformers, Gemini, Euron.one, OpenAI

### Developer Features
- 🛠️ **CLI Tool**: Generate docs from terminal
- 📦 **NPM Package**: Programmatic API access
- 🐳 **Docker Compose**: One-command deployment
- 📈 **Scalable**: Handles 1k → 10k → 50k users
- 🔒 **Secure**: Rate limiting, auth, input validation

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- 8GB RAM (16GB recommended for local LLMs)
- GPU optional (for faster OCR/LLM)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lecture-docs.git
cd lecture-docs
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys (at minimum, add GEMINI_API_KEY or EURON_API_KEY)
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs

That's it! 🎉

(venv) PS C:\Users\asnoi\Downloads\godoc\backend> python -m app.services.job_queue    ---ex for job queue 
(venv) PS C:\Users\asnoi\Downloads\godoc\backend> python -m uvicorn app.main:app --reload --port 8080  -- ex for backend 
PS C:\Users\asnoi\Downloads\godoc\frontend> npm run dev  --- ex for frontend

### Without Docker (Local Development)

See [RUN_LOCALLY.md](./RUN_LOCALLY.md) for detailed instructions.

## 📖 Usage

### Web Interface

1. **Upload Files**: Drag & drop handwritten notes, PDFs, code, or paste YouTube links
2. **Wait for Processing**: OCR, transcription, and AI generation happen automatically
3. **View Documentation**: Beautiful Markdown with examples, explanations, code blocks
4. **Chat with AI**: Ask questions about your notes using the per-project chatbot
5. **Export**: Download as Markdown, PDF, or sync to GitHub

### CLI Tool

```bash
# Install CLI globally
npm install -g lecture-docs-cli

# Generate documentation
lecture-docs generate ./my-notes --output README.md

# Chat with your notes
lecture-docs chat ./project --ask "Explain smart contracts"

# Sync to GitHub
lecture-docs sync --github username/repo
```

### Programmatic API

```typescript
import { LectureDocsClient } from 'lecture-docs-core';

const client = new LectureDocsClient({ apiUrl: 'http://localhost:8080' });

// Upload and process
const project = await client.upload({
  files: ['./notes.jpg', './code.sol'],
  courseName: 'blockchain-101',
  moduleName: 'mod-1',
  lectureName: 'lec-4'
});

// Chat
const response = await client.chat(project.id, 'Explain this concept');
console.log(response);
```

## 🎨 UI Preview

**Vintage Color Palette:**
- Pure Black `#000000` / Pure White `#FFFFFF`
- Dark Gray `#1A1A1A` / Light Gray `#E5E5E5`
- Accent Yellow `#FFC107`

Clean, professional, production-ready design.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Next.js 15 Frontend               │
│     (Upload, Dashboard, Chat UI)            │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      FastAPI Backend (Python)               │
│  ┌─────────────────────────────────────┐   │
│  │  Processing Pipeline                │   │
│  │  • OCR (TrOCR/Tesseract)           │   │
│  │  • STT (Whisper)                   │   │
│  │  • Chunking (smart code-aware)     │   │
│  │  • Embeddings (sentence-trans)     │   │
│  │  • LLM (Gemini/Euron/local)        │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  RAG System (LangChain)            │   │
│  │  • Vector search (Chroma)          │   │
│  │  • Context retrieval               │   │
│  │  • Chatbot responses               │   │
│  └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│          Data Layer                         │
│  • PostgreSQL (metadata)                    │
│  • Redis (cache + queue)                    │
│  • Chroma (embeddings)                      │
│  • File storage (uploads)                   │
└─────────────────────────────────────────────┘
```

## 🔑 API Keys & Setup

### Free Options (Recommended)

1. **Gemini 2.5 Flash** (FREE, 1M tokens/min)
   - Get key: https://aistudio.google.com/app/apikey
   - Add to `.env`: `GEMINI_API_KEY=your_key`

2. **Euron.one** (FREE tier, multiple models)
   - Get key: https://www.euron.one/api-keys
   - Add to `.env`: `EURON_API_KEY=your_key`

3. **Sentence Transformers** (FREE, local embeddings)
   - Auto-downloads on first use
   - No API key needed

### Optional (Paid)

4. **OpenAI** - Better quality, paid
5. **Anthropic Claude** - Best reasoning, paid
6. **Clerk** - User authentication (free tier available)

## 📊 Scalability

### Current Setup (Docker Compose)
- **Handles**: 100-1000 concurrent users
- **Cost**: $0-20/month (just hosting)
- **Deployment**: Single server

### Scaling to 10k Users
- Add load balancer
- Horizontal scaling (3-5 backend instances)
- Separate Redis cluster
- CDN for static assets
- **Cost**: ~$200/month

### Scaling to 50k+ Users
- Kubernetes cluster
- Managed PostgreSQL (AWS RDS)
- Managed Redis (Upstash/ElastiCache)
- Object storage (S3)
- Vector DB cluster (Qdrant Cloud)
- **Cost**: ~$500-1000/month

See [ARCHITECTURE.md](./ARCHITECTURE.md) for details.

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# Integration tests
docker-compose run backend pytest tests/test_integration.py
```

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) first.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](./LICENSE) file.

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- Hugging Face Transformers
- LangChain for RAG orchestration
- Chroma for vector storage
- Next.js and FastAPI teams

## 📞 Support

- 📧 Email: support@lecturedocs.io
- 💬 Discord: [Join our community](https://discord.gg/lecturedocs)
- 🐛 Issues: [GitHub Issues](https://github.com/uzumaki-ak/lecture-docs/issues)
- 📖 Docs: [Full Documentation](https://docs.lecturedocs.io)

---

Made with ❤️ for students learning blockchain and beyond.