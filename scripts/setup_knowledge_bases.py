#!/usr/bin/env python3
"""
Setup script for knowledge bases and initial data
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def create_directories():
    """Create necessary directories"""
    directories = [
        './data/knowledge_bases',
        './data/media_cache',
        './data/audio_cache', 
        './data/output_videos',
        './logs',
        './config'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_knowledge_bases():
    """Initialize knowledge bases"""
    try:
        print("🧠 Setting up knowledge bases...")
        
        # This would normally initialize vector databases
        # For now, just create the directory structure
        chroma_path = './data/knowledge_bases/chroma_db'
        os.makedirs(chroma_path, exist_ok=True)
        
        print("✅ Knowledge base directories created")
        print("💡 Knowledge bases will be initialized on first run")
        
    except Exception as e:
        print(f"❌ Failed to setup knowledge bases: {e}")
        return False
    
    return True

def create_sample_config():
    """Create sample configuration files"""
    try:
        # Create sample YouTube client secret structure
        youtube_config = {
            "web": {
                "client_id": "your-client-id.googleusercontent.com",
                "project_id": "your-project-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_secret": "your-client-secret",
                "redirect_uris": ["http://localhost"]
            }
        }
        
        config_path = './config/youtube_client_secret.json.example'
        with open(config_path, 'w') as f:
            import json
            json.dump(youtube_config, f, indent=2)
        
        print(f"✅ Created sample config: {config_path}")
        print("💡 Copy this to youtube_client_secret.json and update with your credentials")
        
    except Exception as e:
        print(f"❌ Failed to create sample config: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🛠️  Kannada News Automation - Initial Setup")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Create directories
    create_directories()
    
    # Setup knowledge bases  
    if not setup_knowledge_bases():
        return 1
    
    # Create sample configuration
    if not create_sample_config():
        return 1
    
    print("\n🎉 Initial setup completed!")
    print("\n📋 Next steps:")
    print("1. Configure your .env file with all API keys")
    print("2. Set up YouTube OAuth credentials in ./config/")
    print("3. Run 'python scripts/test_elevenlabs.py' to test ElevenLabs")
    print("4. Start development with 'python scripts/run_development.py'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())