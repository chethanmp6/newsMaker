#!/usr/bin/env python3
"""
Basic test script for core functionality without external services
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

async def test_basic_functionality():
    """Test basic functionality without external API calls"""
    print("🧪 Testing basic functionality...")
    
    try:
        # Test imports
        print("1. Testing imports...")
        from kannada_news_automation.config.settings import Settings
        from kannada_news_automation.agents.news_collector import NewsCollectionAgent
        from kannada_news_automation.agents.translator import TranslationAgent
        from kannada_news_automation.agents.content_processor import ContentProcessingAgent
        print("   ✅ All imports successful")
        
        # Test settings
        print("2. Testing settings...")
        settings = Settings()
        print(f"   ✅ Settings loaded: {settings.log_level}")
        
        # Test knowledge base creation (offline)
        print("3. Testing knowledge base creation...")
        collector = NewsCollectionAgent()
        translator = TranslationAgent()
        processor = ContentProcessingAgent()
        print("   ✅ Agents initialized successfully")
        
        # Test basic text processing
        print("4. Testing text processing...")
        test_text = "This is a test news article about Karnataka government announcing new policies."
        
        # Test key point extraction
        key_points = processor._extract_key_points(test_text, max_points=2)
        print(f"   ✅ Key points extracted: {len(key_points)} points")
        
        # Test audio optimization
        optimized_text = processor._optimize_for_audio(test_text)
        print(f"   ✅ Text optimized for audio: {len(optimized_text)} characters")
        
        # Test translation utilities (without API calls)
        category_intro = translator.create_category_intro("karnataka")
        print(f"   ✅ Category intro created: {category_intro}")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_pipeline_structure():
    """Test pipeline structure without external calls"""
    print("\n🔧 Testing pipeline structure...")
    
    try:
        from kannada_news_automation.pipeline import NewsAutomationPipeline
        
        pipeline = NewsAutomationPipeline()
        print("   ✅ Pipeline initialized")
        print(f"   📊 Pipeline stats: {pipeline.stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🎬 Kannada News Automation - Basic Tests")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Run basic tests
    basic_success = await test_basic_functionality()
    pipeline_success = await test_simple_pipeline_structure()
    
    if basic_success and pipeline_success:
        print("\n✅ All basic tests passed! System is ready for development.")
        print("\n📋 To run with real APIs:")
        print("1. Add your actual API keys to .env")
        print("2. Start Redis and PostgreSQL (docker-compose up -d redis postgres)")
        print("3. Run: uv run python src/kannada_news_automation/main.py")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        sys.exit(1)