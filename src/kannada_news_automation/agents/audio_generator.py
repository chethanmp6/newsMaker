try:
    from elevenlabs import generate, Voice, VoiceSettings
except ImportError:
    # Handle different ElevenLabs package versions
    def generate(*args, **kwargs):
        raise NotImplementedError("ElevenLabs API not available - please configure API key")
    
    class Voice:
        def __init__(self, *args, **kwargs):
            pass
    
    class VoiceSettings:
        def __init__(self, *args, **kwargs):
            pass
import os
import asyncio
from pydub import AudioSegment
from llama_index.core import VectorStoreIndex, Document
# from llama_index.core.agent import ReActAgent  # Disabled for compatibility
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AudioGeneratorAgent:
    def __init__(self):
        """Initialize ElevenLabs audio generation with LlamaIndex intelligence"""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
        
        # Voice settings optimized for news delivery
        self.voice_settings = VoiceSettings(
            stability=float(os.getenv("ELEVENLABS_VOICE_STABILITY", "0.5")),
            similarity_boost=float(os.getenv("ELEVENLABS_VOICE_SIMILARITY", "0.8")),
            style=0.0,  # Neutral style for news
            use_speaker_boost=True
        )
        
        # Build knowledge base for audio optimization
        self.audio_kb = self._build_audio_knowledge_base()
        self.audio_engine = self.audio_kb.as_query_engine()
        
        # Create tools for the agent
        self.tools = [
            QueryEngineTool(
                query_engine=self.audio_engine,
                metadata=ToolMetadata(
                    name="audio_optimizer",
                    description="Optimizes audio settings based on content type and requirements"
                )
            ),
            FunctionTool.from_defaults(fn=self._generate_speech),
            FunctionTool.from_defaults(fn=self._adjust_audio_timing),
            FunctionTool.from_defaults(fn=self._optimize_for_category)
        ]
        
        # Simplified without agent for compatibility
        # self.agent = ReActAgent.from_tools(self.tools, verbose=True)
    
    def _build_audio_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for audio generation optimization"""
        documents = [
            Document(text="Political news should use formal, authoritative tone with slower speech rate for clarity and gravitas."),
            Document(text="Sports news benefits from energetic, enthusiastic delivery with faster pace to match excitement."),
            Document(text="Economic news requires clear, measured delivery with emphasis on numbers and key figures."),
            Document(text="International news should maintain neutral, professional tone suitable for global audience."),
            Document(text="Regional news (Karnataka, Tamil Nadu, Andhra, Kerala) can use slightly warmer, more personal tone."),
            Document(text="Breaking news requires urgent, attention-grabbing delivery with emphasis on key facts."),
            Document(text="For 60-second videos, each news segment should be 8-10 seconds, requiring concise, punchy delivery."),
            Document(text="Kannada pronunciation should emphasize clear consonants and proper vowel sounds for better comprehension."),
            Document(text="Audio for mobile viewing (YouTube Shorts) needs higher clarity and slightly boosted volume."),
            Document(text="Transitions between news items should have brief pauses (0.5 seconds) for better segmentation.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    def _optimize_for_category(self, category: str, text: str) -> Dict:
        """Optimize voice settings based on news category"""
        category_settings = {
            "international": {"stability": 0.6, "similarity": 0.8, "speed": 1.0},
            "national": {"stability": 0.7, "similarity": 0.8, "speed": 1.0},
            "karnataka": {"stability": 0.5, "similarity": 0.9, "speed": 1.1},
            "tamilnadu": {"stability": 0.5, "similarity": 0.9, "speed": 1.1},
            "andhra": {"stability": 0.5, "similarity": 0.9, "speed": 1.1},
            "kerala": {"stability": 0.5, "similarity": 0.9, "speed": 1.1}
        }
        
        settings = category_settings.get(category, {"stability": 0.5, "similarity": 0.8, "speed": 1.0})
        
        # Adjust for text length
        word_count = len(text.split())
        if word_count > 100:
            settings["speed"] = min(1.3, settings["speed"] + 0.2)  # Speed up for longer text
        
        return settings
    
    async def _generate_speech(self, text: str, voice_settings: Dict, output_path: str) -> str:
        """Generate speech using ElevenLabs API"""
        try:
            # Optimize text for speech
            optimized_text = self._optimize_text_for_speech(text)
            
            # Create voice settings
            settings = VoiceSettings(
                stability=voice_settings.get("stability", 0.5),
                similarity_boost=voice_settings.get("similarity", 0.8),
                style=0.0,
                use_speaker_boost=True
            )
            
            # Generate audio
            audio = generate(
                text=optimized_text,
                voice=self.voice_id,
                model=self.model_id,
                voice_settings=settings
            )
            
            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(audio)
            
            logger.info(f"Audio generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
    
    def _optimize_text_for_speech(self, text: str) -> str:
        """Optimize text for natural speech delivery"""
        # Add pauses for better pacing
        text = text.replace('.', '... ')
        text = text.replace(',', ', ')
        text = text.replace(':', ': ')
        
        # Handle numbers for better pronunciation
        text = text.replace('%', ' ಶೇಕಡ ')  # Percent in Kannada
        text = text.replace('&', ' ಮತ್ತು ')  # And in Kannada
        
        # Add emphasis markers for important words
        important_words = ['breaking', 'urgent', 'important', 'significant']
        for word in important_words:
            text = text.replace(word.lower(), f"*{word}*")
        
        return text.strip()
    
    async def _adjust_audio_timing(self, audio_path: str, target_duration: float) -> str:
        """Adjust audio timing to fit target duration"""
        try:
            audio = AudioSegment.from_file(audio_path)
            current_duration = len(audio) / 1000.0  # Convert to seconds
            
            if abs(current_duration - target_duration) < 0.5:
                return audio_path  # Already close enough
            
            # Calculate speed adjustment
            speed_factor = current_duration / target_duration
            
            if 0.8 <= speed_factor <= 1.25:  # Reasonable speed adjustment range
                # Adjust speed
                adjusted_audio = audio.speedup(playback_speed=speed_factor)
                
                # Save adjusted audio
                adjusted_path = audio_path.replace('.mp3', '_adjusted.mp3')
                adjusted_audio.export(adjusted_path, format="mp3", bitrate="128k")
                
                logger.info(f"Audio timing adjusted: {current_duration:.2f}s -> {target_duration:.2f}s")
                return adjusted_path
            else:
                logger.warning(f"Speed adjustment too extreme ({speed_factor:.2f}x), keeping original")
                return audio_path
                
        except Exception as e:
            logger.error(f"Error adjusting audio timing: {e}")
            return audio_path
    
    async def generate_kannada_audio(
        self, 
        text: str, 
        category: str, 
        target_duration: Optional[float] = None
    ) -> str:
        """Generate optimized Kannada audio for news content"""
        try:
            # Create output path
            os.makedirs("./data/audio_cache", exist_ok=True)
            output_path = f"./data/audio_cache/{category}_{hash(text) % 10000}.mp3"
            
            # Check cache first
            if os.path.exists(output_path):
                logger.info(f"Using cached audio: {output_path}")
                return output_path
            
            # Use agent to optimize audio generation
            prompt = f"""
            Generate optimized Kannada audio for {category} news:
            Text: {text}
            Target duration: {target_duration or 'flexible'} seconds
            
            Steps:
            1. Use audio_optimizer to determine best settings for {category} news
            2. Optimize text for natural Kannada speech delivery
            3. Generate speech with optimized voice settings
            4. If target duration specified, adjust timing accordingly
            
            Ensure clear pronunciation and appropriate tone for news delivery.
            """
            
            response = await self.agent.achat(prompt)
            
            # Get optimized settings
            voice_settings = self._optimize_for_category(category, text)
            
            # Generate speech
            audio_path = await self._generate_speech(text, voice_settings, output_path)
            
            # Adjust timing if needed
            if target_duration:
                audio_path = await self._adjust_audio_timing(audio_path, target_duration)
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Error generating Kannada audio for {category}: {e}")
            raise
    
    async def generate_batch_audio(self, content_dict: Dict[str, str]) -> Dict[str, str]:
        """Generate audio for multiple news items"""
        # Calculate timing for each segment (60 seconds total)
        timing_allocation = {
            "international": 8,
            "national": 8, 
            "karnataka": 10,  # Priority
            "tamilnadu": 8,
            "andhra": 8,
            "kerala": 8
        }
        
        audio_files = {}
        tasks = []
        
        for category, text in content_dict.items():
            target_duration = timing_allocation.get(category, 8)
            task = self.generate_kannada_audio(text, category, target_duration)
            tasks.append((category, task))
        
        # Generate all audio files concurrently
        for category, task in tasks:
            try:
                audio_path = await task
                audio_files[category] = audio_path
                logger.info(f"Audio generated for {category}: {audio_path}")
            except Exception as e:
                logger.error(f"Failed to generate audio for {category}: {e}")
                audio_files[category] = None
        
        return audio_files