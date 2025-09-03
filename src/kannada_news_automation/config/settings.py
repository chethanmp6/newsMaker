import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str
    elevenlabs_api_key: str
    youtube_api_key: str
    youtube_client_secret_file: str = "./config/youtube_client_secret.json"
    news_api_key: str
    unsplash_api_key: str
    pexels_api_key: str
    
    # ElevenLabs Configuration
    elevenlabs_voice_id: str = "pNInz6obpgDQGcFmaJgB"
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    elevenlabs_voice_stability: float = 0.5
    elevenlabs_voice_similarity: float = 0.8
    elevenlabs_optimize_streaming: bool = False
    
    # Database and Cache
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql://admin:password@localhost:5432/news_automation"
    chroma_db_path: str = "./data/knowledge_bases/chroma_db"
    
    # Audio Settings
    audio_sample_rate: int = 22050
    audio_format: str = "mp3"
    audio_bitrate: int = 128
    target_audio_duration_seconds: int = 60
    
    # Video Settings
    video_resolution: str = "1080x1920"  # YouTube Shorts format
    video_fps: int = 30
    video_bitrate: str = "2000k"
    
    # System Configuration
    pipeline_run_interval_hours: int = 6
    max_news_per_category: int = 1
    video_upload_enabled: bool = True
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'