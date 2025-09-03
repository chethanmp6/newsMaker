from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
import json
from typing import Dict, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class YouTubeUploadAgent:
    def __init__(self):
        """Initialize YouTube upload with OAuth2 authentication"""
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "./config/youtube_client_secret.json")
        self.credentials_file = "./config/youtube_credentials.json"
        
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API using OAuth2"""
        try:
            credentials = None
            
            # Check if we have saved credentials
            if os.path.exists(self.credentials_file):
                credentials = Credentials.from_authorized_user_file(self.credentials_file, self.scopes)
            
            # If credentials are invalid or don't exist, go through OAuth flow
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    if not os.path.exists(self.client_secrets_file):
                        logger.error(f"YouTube client secrets file not found: {self.client_secrets_file}")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, self.scopes
                    )
                    credentials = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.credentials_file, 'w') as token:
                    token.write(credentials.to_json())
            
            # Build YouTube API client
            self.youtube = build(self.api_service_name, self.api_version, credentials=credentials)
            logger.info("YouTube API authentication successful")
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            self.youtube = None
    
    def _generate_seo_optimized_metadata(self, video_metadata: Dict) -> Dict:
        """Generate SEO-optimized title, description, and tags"""
        categories = video_metadata.get('categories', [])
        timestamp = datetime.now().strftime("%B %d, %Y")
        
        # Create engaging title
        if 'karnataka' in categories:
            title = f"Today's Karnataka News in Kannada | {timestamp} | Breaking Updates"
        else:
            title = f"Latest Kannada News Updates | {timestamp} | South India News"
        
        # Create comprehensive description
        description_parts = [
            f"🎥 Today's top news stories in Kannada - {timestamp}",
            "",
            "📰 In this video:",
        ]
        
        for i, category in enumerate(categories, 1):
            category_name = {
                'international': 'International News',
                'national': 'National News', 
                'karnataka': 'Karnataka News',
                'tamilnadu': 'Tamil Nadu News',
                'andhra': 'Andhra Pradesh News',
                'kerala': 'Kerala News'
            }.get(category, category.title())
            
            description_parts.append(f"{i}. {category_name}")
        
        description_parts.extend([
            "",
            "🔔 Subscribe for daily Kannada news updates!",
            "👍 Like if you found this helpful",
            "💬 Comment your thoughts below",
            "",
            "🏷️ Tags:",
            "#KannadaNews #Karnataka #BangaloreNews #SouthIndiaNews #IndiaNews",
            "#KannadaUpdates #NewsInKannada #TodaysNews #BreakingNews",
            "",
            "📱 Follow us for more updates!",
            "",
            f"🎬 Generated with AI technology on {timestamp}",
            "🤖 Automated news compilation with ElevenLabs TTS"
        ])
        
        description = "\n".join(description_parts)
        
        # Generate relevant tags
        base_tags = [
            "Kannada news", "Karnataka news", "Bangalore news", "South India news",
            "India news", "Kannada updates", "news in Kannada", "today's news",
            "breaking news", "latest news", "current affairs", "news update"
        ]
        
        category_specific_tags = {
            'international': ["international news", "world news", "global news"],
            'national': ["national news", "India news", "central government"],
            'karnataka': ["Karnataka", "Bangalore", "Bengaluru", "Karnataka government"],
            'tamilnadu': ["Tamil Nadu", "Chennai", "TN news"],
            'andhra': ["Andhra Pradesh", "Hyderabad", "AP news", "Telangana"],
            'kerala': ["Kerala", "Kochi", "Kerala news"]
        }
        
        for category in categories:
            if category in category_specific_tags:
                base_tags.extend(category_specific_tags[category])
        
        # Remove duplicates and limit to 500 characters (YouTube limit)
        tags = list(set(base_tags))
        tags_string = ", ".join(tags)
        if len(tags_string) > 500:
            # Truncate tags to fit YouTube's limit
            truncated_tags = []
            current_length = 0
            for tag in tags:
                if current_length + len(tag) + 2 <= 500:  # +2 for ", "
                    truncated_tags.append(tag)
                    current_length += len(tag) + 2
                else:
                    break
            tags = truncated_tags
        
        return {
            "title": title,
            "description": description,
            "tags": tags
        }
    
    def _upload_video(self, video_path: str, metadata: Dict) -> Optional[str]:
        """Upload video to YouTube"""
        if not self.youtube:
            logger.error("YouTube API not authenticated")
            return None
        
        try:
            seo_metadata = self._generate_seo_optimized_metadata(metadata)
            
            body = {
                'snippet': {
                    'title': seo_metadata['title'],
                    'description': seo_metadata['description'],
                    'tags': seo_metadata['tags'],
                    'categoryId': '25',  # News & Politics category
                    'defaultLanguage': 'kn',  # Kannada
                    'defaultAudioLanguage': 'kn'
                },
                'status': {
                    'privacyStatus': 'public',
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            # Execute upload
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if response is not None:
                        if 'id' in response:
                            video_id = response['id']
                            logger.info(f"Video uploaded successfully: https://youtu.be/{video_id}")
                            return video_id
                        else:
                            logger.error(f"Upload failed: {response}")
                            return None
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        logger.warning(f"Retryable error: {e}")
                        retry += 1
                        if retry > 3:
                            logger.error("Max retries exceeded")
                            return None
                    else:
                        logger.error(f"Non-retryable error: {e}")
                        return None
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return None
    
    def _set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set custom thumbnail for the video"""
        if not self.youtube or not os.path.exists(thumbnail_path):
            return False
        
        try:
            media = MediaFileUpload(thumbnail_path)
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            )
            request.execute()
            logger.info(f"Thumbnail set for video: {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting thumbnail: {e}")
            return False
    
    def _add_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """Add video to a specific playlist"""
        if not self.youtube:
            return False
        
        try:
            body = {
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
            
            request = self.youtube.playlistItems().insert(
                part='snippet',
                body=body
            )
            request.execute()
            logger.info(f"Video {video_id} added to playlist {playlist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to playlist: {e}")
            return False
    
    async def upload_with_optimization(self, video_path: str, metadata: Dict) -> Dict:
        """Upload video with full optimization and post-processing"""
        try:
            if not os.path.exists(video_path):
                return {
                    "success": False,
                    "error": "Video file not found"
                }
            
            logger.info(f"Starting YouTube upload: {video_path}")
            
            # Upload video
            video_id = self._upload_video(video_path, metadata)
            
            if not video_id:
                return {
                    "success": False,
                    "error": "Video upload failed"
                }
            
            # Additional optimizations
            result = {
                "success": True,
                "video_id": video_id,
                "url": f"https://youtu.be/{video_id}",
                "upload_timestamp": datetime.now().isoformat()
            }
            
            # Set thumbnail if available
            thumbnail_path = video_path.replace('.mp4', '_thumbnail.jpg')
            if os.path.exists(thumbnail_path):
                if self._set_thumbnail(video_id, thumbnail_path):
                    result["thumbnail_set"] = True
            
            # Add to daily news playlist (if configured)
            daily_playlist_id = os.getenv("YOUTUBE_DAILY_PLAYLIST_ID")
            if daily_playlist_id:
                if self._add_to_playlist(video_id, daily_playlist_id):
                    result["added_to_playlist"] = True
            
            logger.info(f"YouTube upload completed successfully: {video_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in upload optimization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_video_analytics(self, video_id: str) -> Dict:
        """Get basic video analytics (views, likes, comments)"""
        if not self.youtube:
            return {"error": "YouTube API not authenticated"}
        
        try:
            request = self.youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            )
            response = request.execute()
            
            if response["items"]:
                item = response["items"][0]
                return {
                    "video_id": video_id,
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "views": int(item["statistics"].get("viewCount", 0)),
                    "likes": int(item["statistics"].get("likeCount", 0)),
                    "comments": int(item["statistics"].get("commentCount", 0)),
                    "duration": item.get("contentDetails", {}).get("duration", "")
                }
            else:
                return {"error": "Video not found"}
                
        except Exception as e:
            logger.error(f"Error getting video analytics: {e}")
            return {"error": str(e)}
    
    def is_authenticated(self) -> bool:
        """Check if YouTube API is properly authenticated"""
        return self.youtube is not None