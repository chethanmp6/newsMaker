# Kannada News Automation System

Automated system for generating 60-second Kannada news video shorts with ElevenLabs TTS and LlamaIndex intelligence.

## Features

- **Intelligent News Collection**: LlamaIndex RAG-powered trending news detection
- **High-Quality Audio**: ElevenLabs multilingual TTS for natural Kannada voices  
- **Automated Video Assembly**: Precise timing and professional transitions
- **YouTube Integration**: SEO-optimized uploads every 6 hours
- **Modern Python**: UV framework for fast dependency management
- **Multi-Agent Architecture**: 7 specialized AI agents for complete automation

## System Architecture

The system uses a sophisticated **7-agent architecture** powered by LlamaIndex:

1. **News Collection Agent** - RAG-powered trending news detection from multiple RSS sources
2. **Content Processing Agent** - Creates video-optimized summaries for 60-second format
3. **Translation Agent** - Cultural context-aware Kannada translation with regional relevance
4. **Audio Generation Agent** - ElevenLabs TTS with category-specific voice optimization
5. **Visual Content Agent** - Copyright-free media collection from Unsplash/Pexels
6. **Video Assembly Agent** - Precise 60-second video creation with professional transitions
7. **YouTube Upload Agent** - SEO-optimized metadata generation and automated upload

## Quick Start

### Prerequisites
- **Python 3.11+**
- **Docker** (for Redis and optional full deployment)
- **API Keys**: OpenAI, ElevenLabs, YouTube, NewsAPI, Unsplash, Pexels

### Local Development Setup

#### Option 1: Easy Development Server (Recommended)

1. **Clone and setup:**
```bash
git clone <repository>
cd newsMaker
```

2. **Install dependencies:**
```bash
# Using UV (recommended)
uv sync

# OR using pip
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Your .env file should contain:
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id
YOUTUBE_API_KEY=your_youtube_key
NEWS_API_KEY=your_news_api_key
UNSPLASH_API_KEY=your_unsplash_key
PEXELS_API_KEY=your_pexels_key
VIDEO_UPLOAD_ENABLED=true
PIPELINE_RUN_INTERVAL_HOURS=6
```

4. **Start the development server:**
```bash
python run_dev_server.py
```

This will:
- ✅ Automatically start Redis with Docker if needed
- ✅ Validate all system components
- ✅ Start FastAPI server with hot reload on http://localhost:8000

#### Option 2: Manual Setup

```bash
# Start Redis manually
docker run -d --name dev-redis -p 6379:6379 redis:7-alpine

# Set Python path and run
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
cd src
python -m kannada_news_automation.main
```

### Docker Deployment

```bash
# Full production deployment
docker-compose up --build -d
```

## API Endpoints

Once running, access these endpoints:

- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Pipeline Status**: http://localhost:8000/pipeline/status
- **System Info**: http://localhost:8000/
- **Recent Logs**: http://localhost:8000/logs
- **Manual Trigger**: `POST /pipeline/trigger`

## Development Commands

```bash
# Install dependencies
uv sync

# Start development server (recommended)
python run_dev_server.py

# Test system components
python -c "
import sys, os
sys.path.insert(0, 'src')
from kannada_news_automation.pipeline import NewsAutomationPipeline
print('✅ Components loaded successfully')
"

# Test ElevenLabs integration
uv run python scripts/test_elevenlabs.py

# Test basic functionality
uv run python scripts/test_basic.py

# Manual pipeline trigger
curl -X POST http://localhost:8000/pipeline/trigger

# Check system health
curl http://localhost:8000/health

# View system statistics
curl http://localhost:8000/pipeline/status
```

## Configuration

### Required Environment Variables

```env
# Core APIs
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_kannada_voice_id

# YouTube Integration
YOUTUBE_API_KEY=your_youtube_api_key

# News & Media Sources
NEWS_API_KEY=your_news_api_key
UNSPLASH_API_KEY=your_unsplash_api_key
PEXELS_API_KEY=your_pexels_api_key

# System Configuration
VIDEO_UPLOAD_ENABLED=true
PIPELINE_RUN_INTERVAL_HOURS=6
```

### Optional Configuration

```env
# Audio Settings
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_VOICE_STABILITY=0.5
ELEVENLABS_VOICE_SIMILARITY=0.8

# Video Settings
VIDEO_RESOLUTION=1080x1920
VIDEO_FPS=30
TARGET_AUDIO_DURATION_SECONDS=60

# Database (for production)
DATABASE_URL=postgresql://admin:password@localhost:5432/news_automation
REDIS_URL=redis://localhost:6379/0
```

## Testing the System

### Basic Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "news_collector": "healthy",
    "audio_generator": "healthy",
    "pipeline": "healthy"
  },
  "timestamp": "2025-09-03T12:00:00"
}
```

### Manual Pipeline Trigger
```bash
curl -X POST http://localhost:8000/pipeline/trigger
```

### View System Information
```bash
curl http://localhost:8000/
```

## Production Features

- **Automated Scheduling**: Runs every 6 hours automatically
- **Health Monitoring**: Comprehensive component health checks
- **Error Handling**: Graceful degradation and retry logic
- **Background Processing**: Celery workers for heavy tasks
- **Data Persistence**: PostgreSQL for production data
- **Containerized**: Complete Docker deployment
- **Logging**: Structured logging with file output

## Output

The system produces:
- **60-second videos** in YouTube Shorts format (1080x1920)
- **High-quality Kannada audio** with natural pronunciation
- **Professional video assembly** with smooth transitions
- **SEO-optimized uploads** with relevant metadata
- **Multi-category coverage** (International, National, Karnataka, etc.)

## Monitoring

- **Health Checks**: `/health` endpoint with detailed component status
- **Pipeline Statistics**: `/pipeline/status` with success rates and metrics
- **Log Monitoring**: `/logs` endpoint for recent system activity
- **Docker Health Checks**: Built-in container health monitoring

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure `PYTHONPATH` includes the `src` directory
2. **Redis Connection**: Ensure Redis is running on localhost:6379
3. **API Key Issues**: Verify all required API keys are set in `.env`
4. **Port Conflicts**: Check if port 8000 is available

### Getting Help

1. Check the health endpoint: http://localhost:8000/health
2. View recent logs: http://localhost:8000/logs
3. Check Docker containers: `docker ps`
4. Verify environment variables: `env | grep -E "(OPENAI|ELEVENLABS|YOUTUBE)"`

## Development Workflow

1. **Start Development**: `python run_dev_server.py`
2. **Make Changes**: Edit code with hot reload enabled
3. **Test Components**: Use `/health` and `/docs` endpoints
4. **Manual Testing**: Trigger pipeline via `/pipeline/trigger`
5. **Production Deploy**: `docker-compose up --build -d`

## License

MIT License