#!/usr/bin/env python3
"""
Development runner script for Kannada News Automation
"""

import os
import sys
import asyncio
import subprocess
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY',
        'YOUTUBE_API_KEY',
        'NEWS_API_KEY',
        'UNSPLASH_API_KEY',
        'PEXELS_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please check your .env file and ensure all API keys are configured.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def start_redis_postgres():
    """Start Redis and PostgreSQL using Docker Compose"""
    try:
        print("🐳 Starting Redis and PostgreSQL...")
        subprocess.run([
            'docker-compose', 'up', '-d', 'redis', 'postgres'
        ], check=True)
        print("✅ Database services started")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to start database services")
        print("💡 Make sure Docker and Docker Compose are installed and running")
        return False

async def test_pipeline():
    """Test the news pipeline"""
    try:
        print("🧪 Testing news pipeline...")
        from kannada_news_automation.pipeline import NewsAutomationPipeline
        
        pipeline = NewsAutomationPipeline()
        
        # Run health check
        health = await pipeline.health_check()
        print(f"📊 Pipeline health: {health['overall']}")
        
        if health['overall'] == 'unhealthy':
            print("❌ Pipeline health check failed")
            if 'error' in health:
                print(f"   Error: {health['error']}")
            return False
        
        print("✅ Pipeline health check passed")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

def start_development_server():
    """Start the development server"""
    try:
        print("🚀 Starting development server...")
        print("🌐 Access the API at: http://localhost:8000")
        print("📚 API docs at: http://localhost:8000/docs")
        print("🔍 Health check at: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server")
        
        subprocess.run([
            'python', '-m', 'uvicorn', 
            'src.kannada_news_automation.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Development server stopped")
    except Exception as e:
        print(f"❌ Failed to start development server: {e}")

async def main():
    """Main development setup and run function"""
    print("🎬 Kannada News Automation - Development Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Start database services
    if not start_redis_postgres():
        return 1
    
    # Test pipeline
    if not await test_pipeline():
        print("⚠️  Pipeline test failed, but continuing with server start...")
    
    # Start development server
    start_development_server()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Development setup interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Development setup failed: {e}")
        sys.exit(1)