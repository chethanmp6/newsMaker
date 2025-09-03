# 🚀 Quick Start Guide

## Kannada News Automation System
Complete production-ready system for generating 60-second Kannada news video shorts.

## ✅ System Status
- ✅ **Project Created**: Full system implemented
- ✅ **Dependencies Installed**: UV package manager setup
- ✅ **Directory Structure**: All folders and files created
- ✅ **Configuration Ready**: Environment templates configured
- ⚠️ **API Keys Required**: Add your API keys to `.env` for full functionality

## 🎯 What's Built

### Core AI Agents (LlamaIndex + ReAct)
1. **News Collection Agent** - RAG-powered trending news detection
2. **Content Processing Agent** - Video-optimized summarization
3. **Translation Agent** - Cultural context-aware Kannada translation
4. **Audio Generation Agent** - ElevenLabs high-quality TTS
5. **Visual Content Agent** - Copyright-free media collection
6. **Video Assembly Agent** - Precise 60-second video creation
7. **YouTube Upload Agent** - SEO-optimized automated uploads

### Infrastructure
- **FastAPI Web Application** with scheduling
- **Docker Configuration** for production deployment
- **Database Integration** (Redis + PostgreSQL)
- **Comprehensive Testing** suite
- **Health Monitoring** and logging

## 🏃‍♂️ Run Locally (3 Options)

### Option 1: Demo Server (No API Keys Required)
```bash
cd kannada_news_automation
uv run python scripts/run_simple_server.py
```
Open: http://localhost:8000

### Option 2: Full System (API Keys Required)
```bash
# 1. Configure API keys
cp .env.example .env
# Edit .env with your API keys

# 2. Start databases
docker-compose up -d redis postgres

# 3. Run development server
uv run python scripts/run_development.py
```

### Option 3: Production Docker
```bash
# Configure .env first, then:
docker-compose up --build
```

## 🔑 Required API Keys

| Service | Purpose | Get API Key |
|---------|---------|-------------|
| **OpenAI** | Content processing, embeddings | https://platform.openai.com/api-keys |
| **ElevenLabs** | Kannada text-to-speech | https://elevenlabs.io/ |
| **YouTube** | Automated uploads | https://console.cloud.google.com/ |
| **NewsAPI** | News aggregation | https://newsapi.org/ |
| **Unsplash** | Copyright-free images | https://unsplash.com/developers |
| **Pexels** | Copyright-free images | https://www.pexels.com/api/ |

## 🔄 Pipeline Process

1. **Collect News** → Trending news from 6 categories (International, National, Karnataka, etc.)
2. **Process Content** → AI-powered summarization for video format
3. **Translate to Kannada** → Cultural context-aware translation
4. **Generate Audio** → ElevenLabs TTS with voice optimization
5. **Collect Media** → Copyright-free images from Unsplash/Pexels  
6. **Assemble Video** → 60-second professionally timed video
7. **Upload to YouTube** → SEO-optimized with metadata

## 🎬 Usage

### Manual Trigger
```bash
curl -X POST http://localhost:8000/pipeline/trigger
```

### Automated Scheduling
- Runs every 6 hours automatically
- Configure in `.env`: `PIPELINE_RUN_INTERVAL_HOURS=6`

### Monitoring
- Health: http://localhost:8000/health
- Status: http://localhost:8000/pipeline/status
- Logs: http://localhost:8000/logs

## 🛠️ Development

### Test ElevenLabs Integration
```bash
uv run python scripts/test_elevenlabs.py
```

### Run Tests
```bash
uv run pytest
```

### Project Info
```bash
uv run python scripts/show_project_info.py
```

## 📱 Output

The system generates:
- **60-second videos** in YouTube Shorts format (1080x1920)
- **High-quality Kannada audio** with natural pronunciation
- **SEO-optimized YouTube uploads** with metadata
- **Professional video assembly** with transitions and timing

## 🎉 Ready for Production!

The system is fully production-ready with:
- Docker containerization
- Health monitoring
- Error handling
- Scalable architecture
- Comprehensive logging

Just add your API keys and deploy! 🚀