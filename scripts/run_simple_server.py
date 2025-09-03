#!/usr/bin/env python3
"""
Simple server runner without external dependencies
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def create_simple_app():
    """Create a simple FastAPI app for demonstration"""
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import logging
    from datetime import datetime
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    app = FastAPI(
        title="Kannada News Automation",
        description="Automated Kannada news shorts generation system",
        version="1.0.0-demo"
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with system information"""
        return {
            "message": "Kannada News Automation System - Demo Mode",
            "version": "1.0.0-demo",
            "status": "running",
            "mode": "demonstration",
            "timestamp": datetime.now().isoformat(),
            "features": [
                "LlamaIndex intelligent content processing",
                "ElevenLabs high-quality Kannada TTS",
                "Automated video assembly",
                "YouTube upload with SEO optimization"
            ],
            "note": "Add real API keys to .env for full functionality"
        }
    
    @app.get("/health")
    async def health_check():
        """Simple health check"""
        return {
            "status": "healthy",
            "mode": "demo",
            "timestamp": datetime.now().isoformat(),
            "message": "System running in demo mode"
        }
    
    @app.get("/status")
    async def status():
        """System status"""
        return {
            "system": "Kannada News Automation",
            "mode": "demo",
            "components": {
                "web_server": "running",
                "news_collector": "requires OpenAI API key",
                "audio_generator": "requires ElevenLabs API key",
                "video_assembler": "ready",
                "youtube_uploader": "requires YouTube API key"
            },
            "setup_required": [
                "OpenAI API key for news processing",
                "ElevenLabs API key for Kannada TTS",
                "YouTube API credentials for uploads",
                "Redis and PostgreSQL databases"
            ]
        }
    
    @app.post("/demo/trigger")
    async def demo_trigger():
        """Demo pipeline trigger"""
        return {
            "message": "Demo pipeline triggered",
            "note": "This is a demonstration. Configure API keys for real functionality.",
            "steps": [
                "✅ Web server running",
                "❌ News collection (requires OpenAI API)",
                "❌ Content processing (requires OpenAI API)", 
                "❌ Kannada translation (requires OpenAI API)",
                "❌ Audio generation (requires ElevenLabs API)",
                "❌ Visual content (requires Unsplash/Pexels API)",
                "❌ Video assembly (requires media)",
                "❌ YouTube upload (requires YouTube API)"
            ]
        }
    
    return app

def main():
    """Main function to run the demo server"""
    print("🎬 Kannada News Automation - Demo Server")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    try:
        # Create the app
        app = create_simple_app()
        
        # Import uvicorn here to avoid dependency issues
        import uvicorn
        
        print("🚀 Starting demo server...")
        print("🌐 Open your browser to: http://localhost:8000")
        print("📚 API documentation: http://localhost:8000/docs")
        print("💡 This is a demo version. Add API keys to .env for full functionality.")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Demo server stopped")
        return 0
    except Exception as e:
        print(f"❌ Failed to start demo server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())