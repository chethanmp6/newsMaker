from moviepy.editor import *
import os
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoAssemblyAgent:
    def __init__(self):
        """Initialize video assembly with precise timing controls"""
        self.output_resolution = (1080, 1920)  # 9:16 aspect ratio for YouTube Shorts
        self.fps = 30
        self.target_duration = 60  # seconds
        self.segment_durations = {
            "international": 8,
            "national": 8,
            "karnataka": 10,  # Priority segment
            "tamilnadu": 8,
            "andhra": 8,
            "kerala": 8
        }
    
    def _create_text_clip(
        self, 
        text: str, 
        duration: float, 
        position: str = "center",
        fontsize: int = 50,
        color: str = "white"
    ) -> TextClip:
        """Create styled text clip for titles and overlays"""
        return TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font="Arial-Bold",
            stroke_color="black",
            stroke_width=2
        ).set_duration(duration).set_position(position)
    
    def _prepare_image_clip(
        self, 
        image_path: str, 
        duration: float, 
        effect: str = "zoom"
    ) -> VideoClip:
        """Prepare image clip with effects for video segment"""
        try:
            # Load and resize image
            clip = ImageClip(image_path).set_duration(duration)
            
            # Resize to fit 9:16 aspect ratio
            clip = clip.resize(height=self.output_resolution[1])
            
            # Center crop if needed
            if clip.w > self.output_resolution[0]:
                clip = clip.crop(
                    x_center=clip.w/2,
                    width=self.output_resolution[0]
                )
            
            # Apply effects
            if effect == "zoom":
                # Subtle zoom effect
                clip = clip.resize(lambda t: 1 + 0.02 * t)
            elif effect == "pan":
                # Subtle pan effect
                clip = clip.set_position(lambda t: ('center', 'center'))
            
            return clip
            
        except Exception as e:
            logger.error(f"Error preparing image clip {image_path}: {e}")
            # Return colored background as fallback
            return ColorClip(
                size=self.output_resolution,
                color=(50, 50, 50),
                duration=duration
            )
    
    def _create_news_segment(
        self,
        category: str,
        audio_path: str,
        media_items: List[Dict],
        title_text: str
    ) -> VideoClip:
        """Create a complete news segment with audio and visuals"""
        try:
            segment_duration = self.segment_durations.get(category, 8)
            
            # Load audio
            if audio_path and os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                # Trim or pad audio to match segment duration
                if audio_clip.duration > segment_duration:
                    audio_clip = audio_clip.subclip(0, segment_duration)
                else:
                    # Pad with silence if needed
                    silence_duration = segment_duration - audio_clip.duration
                    if silence_duration > 0:
                        silence = AudioClip(lambda t: 0, duration=silence_duration)
                        audio_clip = concatenate_audioclips([audio_clip, silence])
            else:
                # Create silent audio if no audio file
                logger.warning(f"No audio file for {category}, creating silent segment")
                audio_clip = AudioClip(lambda t: 0, duration=segment_duration)
            
            # Prepare visual clips
            visual_clips = []
            
            if media_items and any(item.get('local_path') for item in media_items):
                # Use provided media
                valid_media = [item for item in media_items if item.get('local_path') and os.path.exists(item['local_path'])]
                
                if valid_media:
                    clips_per_image = segment_duration / len(valid_media)
                    
                    for i, media_item in enumerate(valid_media):
                        image_clip = self._prepare_image_clip(
                            media_item['local_path'],
                            clips_per_image,
                            effect="zoom" if i % 2 == 0 else "pan"
                        )
                        visual_clips.append(image_clip)
                else:
                    # Fallback to colored background
                    visual_clips.append(ColorClip(
                        size=self.output_resolution,
                        color=(30, 50, 80),
                        duration=segment_duration
                    ))
            else:
                # Create category-themed background
                category_colors = {
                    "international": (40, 60, 100),
                    "national": (100, 50, 40),
                    "karnataka": (80, 40, 100),
                    "tamilnadu": (40, 100, 60),
                    "andhra": (100, 80, 40),
                    "kerala": (60, 100, 40)
                }
                color = category_colors.get(category, (50, 50, 50))
                visual_clips.append(ColorClip(
                    size=self.output_resolution,
                    color=color,
                    duration=segment_duration
                ))
            
            # Combine visual clips
            if len(visual_clips) > 1:
                video_clip = concatenate_videoclips(visual_clips)
            else:
                video_clip = visual_clips[0]
            
            # Add category title
            title_clip = self._create_text_clip(
                category.upper(),
                duration=2.0,
                position=("center", 100),
                fontsize=40,
                color="white"
            )
            
            # Compose final segment
            final_segment = CompositeVideoClip([
                video_clip,
                title_clip
            ]).set_audio(audio_clip).set_duration(segment_duration)
            
            logger.info(f"Created segment for {category}: {segment_duration}s")
            return final_segment
            
        except Exception as e:
            logger.error(f"Error creating segment for {category}: {e}")
            # Return fallback segment
            fallback_audio = AudioClip(lambda t: 0, duration=8)
            fallback_video = ColorClip(
                size=self.output_resolution,
                color=(100, 100, 100),
                duration=8
            )
            error_text = self._create_text_clip(
                f"{category.upper()}\nCONTENT ERROR",
                duration=8,
                fontsize=36
            )
            
            return CompositeVideoClip([
                fallback_video,
                error_text
            ]).set_audio(fallback_audio)
    
    def _create_intro_segment(self) -> VideoClip:
        """Create intro segment for the video"""
        intro_duration = 3.0
        
        # Create intro background
        intro_bg = ColorClip(
            size=self.output_resolution,
            color=(20, 30, 50),
            duration=intro_duration
        )
        
        # Create intro text
        title_text = self._create_text_clip(
            "ಕನ್ನಡ ನ್ಯೂಸ್\nKANNADA NEWS",
            duration=intro_duration,
            fontsize=60,
            color="gold"
        )
        
        subtitle_text = self._create_text_clip(
            datetime.now().strftime("%B %d, %Y"),
            duration=intro_duration,
            position=("center", "bottom"),
            fontsize=30,
            color="white"
        )
        
        # Create silent audio
        intro_audio = AudioClip(lambda t: 0, duration=intro_duration)
        
        return CompositeVideoClip([
            intro_bg,
            title_text,
            subtitle_text
        ]).set_audio(intro_audio)
    
    def _create_outro_segment(self) -> VideoClip:
        """Create outro segment for the video"""
        outro_duration = 2.0
        
        # Create outro background
        outro_bg = ColorClip(
            size=self.output_resolution,
            color=(30, 20, 50),
            duration=outro_duration
        )
        
        # Create outro text
        outro_text = self._create_text_clip(
            "ಧನ್ಯವಾದಗಳು\nTHANK YOU",
            duration=outro_duration,
            fontsize=50,
            color="gold"
        )
        
        subscribe_text = self._create_text_clip(
            "SUBSCRIBE FOR MORE NEWS",
            duration=outro_duration,
            position=("center", "bottom"),
            fontsize=25,
            color="white"
        )
        
        # Create silent audio
        outro_audio = AudioClip(lambda t: 0, duration=outro_duration)
        
        return CompositeVideoClip([
            outro_bg,
            outro_text,
            subscribe_text
        ]).set_audio(outro_audio)
    
    async def create_complete_video(
        self,
        audio_files: Dict[str, str],
        media_collections: Dict[str, List[Dict]],
        metadata: Dict
    ) -> str:
        """Assemble complete 60-second news video"""
        try:
            logger.info("Starting video assembly...")
            
            # Create output directory
            os.makedirs("./data/output_videos", exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./data/output_videos/kannada_news_{timestamp}.mp4"
            
            # Create video segments
            segments = []
            
            # Add intro
            intro = self._create_intro_segment()
            segments.append(intro)
            
            # Process each category with valid audio
            total_content_duration = 0
            categories_to_process = [cat for cat in audio_files.keys() if audio_files[cat]]
            
            for category in categories_to_process:
                audio_path = audio_files[category]
                media_items = media_collections.get(category, [])
                title_text = category.upper()
                
                segment = self._create_news_segment(
                    category,
                    audio_path,
                    media_items,
                    title_text
                )
                segments.append(segment)
                total_content_duration += self.segment_durations.get(category, 8)
            
            # Add outro if there's time
            if total_content_duration < 55:  # Leave room for outro
                outro = self._create_outro_segment()
                segments.append(outro)
            
            # Concatenate all segments
            if segments:
                final_video = concatenate_videoclips(segments, method="compose")
                
                # Ensure video doesn't exceed 60 seconds
                if final_video.duration > 60:
                    final_video = final_video.subclip(0, 60)
                
                # Export video
                logger.info(f"Exporting video to {output_path}...")
                final_video.write_videofile(
                    output_path,
                    fps=self.fps,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None  # Suppress MoviePy logging
                )
                
                # Clean up
                final_video.close()
                for segment in segments:
                    segment.close()
                
                logger.info(f"Video assembled successfully: {output_path}")
                logger.info(f"Final duration: {final_video.duration:.2f} seconds")
                
                return output_path
            else:
                logger.error("No video segments created")
                return None
                
        except Exception as e:
            logger.error(f"Error assembling video: {e}")
            return None
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get information about the assembled video"""
        try:
            if not os.path.exists(video_path):
                return {"error": "Video file not found"}
            
            clip = VideoFileClip(video_path)
            info = {
                "duration": clip.duration,
                "resolution": f"{clip.w}x{clip.h}",
                "fps": clip.fps,
                "file_size": os.path.getsize(video_path),
                "has_audio": clip.audio is not None
            }
            clip.close()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {"error": str(e)}