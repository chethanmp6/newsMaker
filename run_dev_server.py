#!/usr/bin/env python3
"""
Development server for the Kannada News Automation System
Run this script to start the FastAPI server locally for development and testing.
"""

import sys
import os
import subprocess
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_redis():
    """Check if Redis is running locally."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print("❌ Redis is not running. Starting Redis with Docker...")
        try:
            subprocess.run(["docker", "run", "-d", "--name", "dev-redis", "-p", "6379:6379", "redis:7-alpine"], check=True)
            print("✅ Redis started successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to start Redis. Please install and start Redis manually.")
            return False

def main():
    print("🚀 Starting Kannada News Automation Development Server")
    print("=" * 50)
    
    # Check Redis
    if not check_redis():
        print("Please start Redis and try again.")
        sys.exit(1)
    
    # Import the FastAPI app
    try:
        from kannada_news_automation.main import app
        print("✅ Application imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        sys.exit(1)
    
    # Start the development server
    print("🌐 Starting FastAPI development server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📍 API documentation: http://localhost:8000/docs")
    print("📍 Health check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        "kannada_news_automation.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()