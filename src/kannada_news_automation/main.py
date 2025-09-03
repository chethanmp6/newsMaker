import os
import logging
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from celery import Celery
from celery.schedules import crontab
import schedule
import time
import threading
from contextlib import asynccontextmanager

import sys
import os
# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kannada_news_automation.pipeline import NewsAutomationPipeline
from kannada_news_automation.config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs('./logs', exist_ok=True)

# Initialize settings
settings = Settings()

# Celery configuration
celery_app = Celery(
    'kannada_news_automation',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['src.kannada_news_automation.tasks']
)

# Celery beat schedule - run every 6 hours
celery_app.conf.beat_schedule = {
    'run-news-pipeline': {
        'task': 'src.kannada_news_automation.tasks.run_pipeline_task',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
}
celery_app.conf.timezone = 'Asia/Kolkata'

# Global pipeline instance
pipeline = NewsAutomationPipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Kannada News Automation System")
    
    # Perform startup checks
    try:
        health = await pipeline.health_check()
        if health["overall"] != "healthy":
            logger.warning(f"System started with health issues: {health}")
        else:
            logger.info("All systems healthy")
    except Exception as e:
        logger.error(f"Startup health check failed: {e}")
    
    yield
    
    logger.info("Shutting down Kannada News Automation System")

# FastAPI app
app = FastAPI(
    title="Kannada News Automation",
    description="Automated Kannada news shorts generation with ElevenLabs TTS",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Kannada News Automation System",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "LlamaIndex intelligent content processing",
            "ElevenLabs high-quality Kannada TTS",
            "Automated video assembly",
            "YouTube upload with SEO optimization"
        ]
    }

@app.post("/pipeline/trigger")
async def trigger_pipeline(background_tasks: BackgroundTasks):
    """Manually trigger the news pipeline"""
    try:
        logger.info("Manual pipeline trigger requested")
        
        # Run pipeline in background
        task_id = f"manual_{int(time.time())}"
        background_tasks.add_task(run_pipeline_background, task_id)
        
        return {
            "message": "Pipeline triggered successfully",
            "task_id": task_id,
            "status": "started"
        }
    except Exception as e:
        logger.error(f"Failed to trigger pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/status")
async def get_pipeline_status():
    """Get current pipeline status and statistics"""
    return {
        "stats": pipeline.stats,
        "last_run": pipeline.stats.get("last_run"),
        "success_rate": pipeline.stats["successes"] / max(1, pipeline.stats["runs"]) * 100
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        health = await pipeline.health_check()
        status_code = 200 if health["overall"] == "healthy" else 503
        return JSONResponse(content=health, status_code=status_code)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={"overall": "unhealthy", "error": str(e)},
            status_code=503
        )

@app.get("/logs")
async def get_recent_logs(lines: int = 100):
    """Get recent log entries"""
    try:
        with open('./logs/app.log', 'r') as f:
            log_lines = f.readlines()
        
        recent_logs = log_lines[-lines:]
        return {"logs": recent_logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read logs: {e}")

async def run_pipeline_background(task_id: str):
    """Run pipeline in background"""
    try:
        logger.info(f"Starting background pipeline task: {task_id}")
        result = await pipeline.run_complete_pipeline()
        logger.info(f"Background pipeline task {task_id} completed: {result['success']}")
        return result
    except Exception as e:
        logger.error(f"Background pipeline task {task_id} failed: {e}")
        return {"success": False, "error": str(e)}

def run_scheduled_pipeline():
    """Run scheduled pipeline using Python schedule"""
    def job():
        logger.info("Scheduled pipeline run starting...")
        try:
            # Run the async pipeline in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(pipeline.run_complete_pipeline())
            loop.close()
            
            logger.info(f"Scheduled pipeline completed: {result['success']}")
        except Exception as e:
            logger.error(f"Scheduled pipeline failed: {e}")
    
    # Schedule every 6 hours
    schedule.every(6).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler():
    """Start the background scheduler"""
    scheduler_thread = threading.Thread(target=run_scheduled_pipeline, daemon=True)
    scheduler_thread.start()
    logger.info("Background scheduler started")

if __name__ == "__main__":
    import uvicorn
    
    # Start background scheduler
    start_scheduler()
    
    # Run FastAPI server
    uvicorn.run(
        "src.kannada_news_automation.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable in production
        log_level="info"
    )