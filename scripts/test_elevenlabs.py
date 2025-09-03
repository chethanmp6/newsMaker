#!/usr/bin/env python3
"""
Test script for ElevenLabs integration
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kannada_news_automation.agents.audio_generator import AudioGeneratorAgent

async def test_elevenlabs_integration():
    """Test ElevenLabs TTS integration"""
    
    load_dotenv()
    
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("❌ ELEVENLABS_API_KEY not found in environment")
        return False
    
    try:
        print("🎤 Testing ElevenLabs integration...")
        
        # Initialize audio generator
        audio_agent = AudioGeneratorAgent()
        
        # Test Kannada text
        test_texts = {
            "simple": "ಇದು ಪರೀಕ್ಷೆ",  # This is a test
            "news": "ಬೆಂಗಳೂರಿನಲ್ಲಿ ಇಂದು ಮಳೆ ಬಿದ್ದಿತು",  # It rained in Bangalore today
            "complex": "ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಹೊಸ ನೀತಿ ಘೋಷಿಸಿದೆ"  # Karnataka government announced new policy
        }
        
        print("📝 Testing different Kannada text samples...")
        
        for test_name, text in test_texts.items():
            print(f"   Testing {test_name}: {text}")
            
            try:
                audio_file = await audio_agent.generate_kannada_audio(
                    text, 
                    "karnataka", 
                    target_duration=3.0
                )
                
                if audio_file and os.path.exists(audio_file):
                    file_size = os.path.getsize(audio_file)
                    print(f"   ✅ Generated: {audio_file} ({file_size} bytes)")
                else:
                    print(f"   ❌ Failed to generate audio for {test_name}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error generating {test_name}: {e}")
                return False
        
        print("🎉 All ElevenLabs tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ElevenLabs integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_elevenlabs_integration())
    sys.exit(0 if success else 1)