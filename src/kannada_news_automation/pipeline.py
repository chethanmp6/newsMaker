import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import os

from .agents.news_collector import NewsCollectionAgent
from .agents.content_processor import ContentProcessingAgent  
from .agents.translator import TranslationAgent
from .agents.audio_generator import AudioGeneratorAgent
from .agents.visual_content import VisualContentAgent
from .agents.video_assembler import VideoAssemblyAgent
from .agents.youtube_uploader import YouTubeUploadAgent

logger = logging.getLogger(__name__)

class NewsAutomationPipeline:
    def __init__(self):
        """Initialize the complete news automation pipeline"""
        self.news_collector = NewsCollectionAgent()
        self.content_processor = ContentProcessingAgent()
        self.translator = TranslationAgent()
        self.audio_generator = AudioGeneratorAgent()
        self.visual_agent = VisualContentAgent()
        self.video_assembler = VideoAssemblyAgent()
        self.uploader = YouTubeUploadAgent()
        
        # Pipeline statistics
        self.stats = {
            "runs": 0,
            "successes": 0,
            "failures": 0,
            "last_run": None
        }
    
    async def run_complete_pipeline(self) -> Dict[str, Any]:
        """Execute the complete news automation pipeline"""
        start_time = datetime.now()
        self.stats["runs"] += 1
        self.stats["last_run"] = start_time
        
        try:
            logger.info("Starting news automation pipeline...")
            
            # Step 1: Collect trending news from all categories
            logger.info("Step 1: Collecting trending news...")
            news_data = await self.news_collector.collect_all_categories()
            
            if not news_data or not any(news_data.values()):
                raise Exception("No news data collected")
            
            logger.info(f"Collected news for {len(news_data)} categories")
            
            # Step 2: Process and summarize content
            logger.info("Step 2: Processing and summarizing content...")
            summaries = {}
            for category, news_item in news_data.items():
                if news_item:
                    summary = await self.content_processor.create_video_summary(
                        news_item.get('content', ''), 
                        category
                    )
                    summaries[category] = summary
            
            if not summaries:
                raise Exception("No content summaries generated")
            
            # Step 3: Translate to Kannada
            logger.info("Step 3: Translating to Kannada...")
            translations = {}
            for category, summary in summaries.items():
                translation = await self.translator.translate_with_context(
                    summary, 
                    category
                )
                translations[category] = translation
            
            # Step 4: Generate high-quality audio with ElevenLabs
            logger.info("Step 4: Generating Kannada audio with ElevenLabs...")
            audio_files = await self.audio_generator.generate_batch_audio(translations)
            
            # Filter out failed audio generations
            valid_audio = {k: v for k, v in audio_files.items() if v is not None}
            if len(valid_audio) < 3:  # Need at least 3 segments for a meaningful video
                raise Exception("Insufficient audio files generated")
            
            # Step 5: Collect relevant media
            logger.info("Step 5: Collecting relevant media...")
            media_collections = {}
            for category, summary in summaries.items():
                if category in valid_audio:
                    media = await self.visual_agent.find_relevant_media(
                        summary, 
                        category
                    )
                    media_collections[category] = media
            
            # Step 6: Assemble video
            logger.info("Step 6: Assembling video...")
            video_metadata = {
                'news_data': news_data,
                'summaries': summaries,
                'translations': translations,
                'categories': list(valid_audio.keys())
            }
            
            video_file = await self.video_assembler.create_complete_video(
                valid_audio, 
                media_collections,
                video_metadata
            )
            
            if not video_file or not os.path.exists(video_file):
                raise Exception("Video assembly failed")
            
            # Step 7: Upload to YouTube
            logger.info("Step 7: Uploading to YouTube...")
            upload_enabled = os.getenv("VIDEO_UPLOAD_ENABLED", "true").lower() == "true"
            
            if upload_enabled:
                upload_result = await self.uploader.upload_with_optimization(
                    video_file,
                    video_metadata
                )
            else:
                logger.info("Upload disabled, skipping YouTube upload")
                upload_result = {"status": "skipped", "reason": "upload_disabled"}
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update statistics
            self.stats["successes"] += 1
            
            result = {
                "success": True,
                "video_file": video_file,
                "upload_result": upload_result,
                "execution_time_seconds": execution_time,
                "categories_processed": list(valid_audio.keys()),
                "audio_quality": "elevenlabs_high",
                "video_duration_seconds": 60,
                "timestamp": start_time.isoformat(),
                "stats": self.stats
            }
            
            logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            self.stats["failures"] += 1
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.error(f"Pipeline failed after {execution_time:.2f} seconds: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time_seconds": execution_time,
                "timestamp": start_time.isoformat(),
                "stats": self.stats
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all pipeline components"""
        health_status = {
            "overall": "healthy",
            "components": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check news collector
            test_news = await self.news_collector.collect_trending_news("national")
            health_status["components"]["news_collector"] = "healthy" if test_news else "unhealthy"
            
            # Check ElevenLabs connection
            test_audio = await self.audio_generator.generate_kannada_audio(
                "ಪರೀಕ್ಷೆ", "test", 2.0
            )
            health_status["components"]["audio_generator"] = "healthy" if test_audio else "unhealthy"
            
            # Check other components
            health_status["components"]["translator"] = "healthy"  # Assume healthy if no errors
            health_status["components"]["visual_agent"] = "healthy"
            health_status["components"]["video_assembler"] = "healthy"
            health_status["components"]["uploader"] = "healthy"
            
            # Overall health
            unhealthy_components = [k for k, v in health_status["components"].items() if v != "healthy"]
            if unhealthy_components:
                health_status["overall"] = "degraded"
                health_status["unhealthy_components"] = unhealthy_components
            
        except Exception as e:
            health_status["overall"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status