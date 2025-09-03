import pytest
import asyncio
from unittest.mock import Mock, patch
from src.kannada_news_automation.pipeline import NewsAutomationPipeline

@pytest.fixture
def pipeline():
    return NewsAutomationPipeline()

@pytest.mark.asyncio
async def test_pipeline_health_check(pipeline):
    """Test pipeline health check functionality"""
    health = await pipeline.health_check()
    assert "overall" in health
    assert "components" in health
    assert health["overall"] in ["healthy", "degraded", "unhealthy"]

@pytest.mark.asyncio
async def test_pipeline_complete_run_mock(pipeline):
    """Test complete pipeline run with mocked components"""
    
    # Mock all agents
    with patch.object(pipeline.news_collector, 'collect_all_categories') as mock_news, \
         patch.object(pipeline.content_processor, 'create_video_summary') as mock_process, \
         patch.object(pipeline.translator, 'translate_with_context') as mock_translate, \
         patch.object(pipeline.audio_generator, 'generate_batch_audio') as mock_audio, \
         patch.object(pipeline.visual_agent, 'find_relevant_media') as mock_visual, \
         patch.object(pipeline.video_assembler, 'create_complete_video') as mock_video, \
         patch.object(pipeline.uploader, 'upload_with_optimization') as mock_upload:
        
        # Set up mocks
        mock_news.return_value = {
            "karnataka": {"title": "Test News", "content": "Test content"}
        }
        mock_process.return_value = "Test summary"
        mock_translate.return_value = "ಪರೀಕ್ಷಾ ಸುದ್ದಿ"
        mock_audio.return_value = {"karnataka": "/path/to/audio.mp3"}
        mock_visual.return_value = [{"url": "test.jpg"}]
        mock_video.return_value = "/path/to/video.mp4"
        mock_upload.return_value = {"status": "success", "video_id": "test123"}
        
        # Run pipeline
        result = await pipeline.run_complete_pipeline()
        
        # Assertions
        assert result["success"] == True
        assert "video_file" in result
        assert "execution_time_seconds" in result
        assert mock_news.called
        assert mock_audio.called

@pytest.mark.asyncio 
async def test_pipeline_failure_handling(pipeline):
    """Test pipeline failure handling"""
    
    # Mock news collector to fail
    with patch.object(pipeline.news_collector, 'collect_all_categories') as mock_news:
        mock_news.side_effect = Exception("News collection failed")
        
        result = await pipeline.run_complete_pipeline()
        
        assert result["success"] == False
        assert "error" in result
        assert "News collection failed" in result["error"]