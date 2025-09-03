# Kannada News Automation System

Automated system for generating 60-second Kannada news video shorts with ElevenLabs TTS and LlamaIndex intelligence.

## Features

- **Intelligent News Collection**: LlamaIndex RAG-powered trending news detection
- **High-Quality Audio**: ElevenLabs multilingual TTS for natural Kannada voices  
- **Automated Video Assembly**: Precise timing and professional transitions
- **YouTube Integration**: SEO-optimized uploads every 6 hours
- **Modern Python**: UV framework for fast dependency management

## Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- API keys for: OpenAI, ElevenLabs, YouTube, NewsAPI, Unsplash, Pexels

### Installation

1. Install UV framework:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone and setup:
```bash
git clone <repository>
cd kannada-news-automation
uv sync
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run with Docker:
```bash
docker-compose up --build
```

## Development Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run python src/kannada_news_automation/main.py

# Run tests
uv run pytest

# Test ElevenLabs integration
uv run python scripts/test_elevenlabs.py

# Manual pipeline trigger
curl -X POST http://localhost:8000/pipeline/trigger

# Check system health
curl http://localhost:8000/health
```

## API Endpoints

- `GET /` - System information
- `POST /pipeline/trigger` - Manual pipeline trigger
- `GET /pipeline/status` - Pipeline statistics
- `GET /health` - Health check
- `GET /logs` - Recent logs

## System Architecture

The system uses a multi-agent architecture with LlamaIndex:

1. **News Collection Agent** - Collects trending news with RAG intelligence
2. **Content Processing Agent** - Creates video-optimized summaries
3. **Translation Agent** - Cultural context-aware Kannada translation
4. **Audio Generation Agent** - ElevenLabs TTS with voice optimization
5. **Visual Content Agent** - Copyright-free media collection
6. **Video Assembly Agent** - Precise timing and professional assembly
7. **YouTube Upload Agent** - SEO optimization and automated upload

## Configuration

Key environment variables:
```env
OPENAI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=voice_id_for_kannada
YOUTUBE_API_KEY=your_key
VIDEO_UPLOAD_ENABLED=true
PIPELINE_RUN_INTERVAL_HOURS=6
```

## Monitoring

- Health checks at `/health`
- Pipeline statistics at `/pipeline/status`
- Log monitoring via `/logs` endpoint
- Docker health checks included

## Production Deployment

1. Set environment variables in `.env`
2. Configure YouTube OAuth credentials
3. Run with Docker Compose:

```bash
docker-compose -f docker-compose.yml up -d
```

## License

MIT License