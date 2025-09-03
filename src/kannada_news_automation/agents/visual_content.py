from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.openai import OpenAI
# from llama_index.core.agent import ReActAgent  # Disabled for compatibility
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
import asyncio
import aiohttp
import requests
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class VisualContentAgent:
    def __init__(self):
        """Initialize visual content collection with copyright-free sources"""
        self.llm = OpenAI(model="gpt-4")
        self.visual_kb = self._build_visual_knowledge_base()
        self.media_kb = self._build_media_knowledge_base()
        
        # API keys
        self.unsplash_key = os.getenv("UNSPLASH_API_KEY")
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        
        # Create query engines
        self.visual_engine = self.visual_kb.as_query_engine()
        self.media_engine = self.media_kb.as_query_engine()
        
        # Create tools
        self.tools = [
            QueryEngineTool(
                query_engine=self.visual_engine,
                metadata=ToolMetadata(
                    name="visual_concept_mapper",
                    description="Maps news content to relevant visual concepts"
                )
            ),
            QueryEngineTool(
                query_engine=self.media_engine,
                metadata=ToolMetadata(
                    name="media_selector",
                    description="Selects appropriate media types for news categories"
                )
            ),
            FunctionTool.from_defaults(fn=self._search_unsplash),
            FunctionTool.from_defaults(fn=self._search_pexels),
            FunctionTool.from_defaults(fn=self._download_media)
        ]
        
        # Simplified without agent for compatibility
        # self.agent = ReActAgent.from_tools(self.tools, llm=self.llm, verbose=True)
    
    def _build_visual_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for visual concept mapping"""
        documents = [
            Document(text="Political news visuals should include government buildings, official meetings, or symbolic imagery like flags."),
            Document(text="Economic news works well with business district shots, market imagery, currency symbols, or charts/graphs."),
            Document(text="Technology news should feature modern cityscapes, office buildings, computer/mobile device imagery."),
            Document(text="International news can use world maps, airplane imagery, or landmark buildings from relevant countries."),
            Document(text="Regional Karnataka news benefits from Bangalore skyline, tech parks, or cultural landmarks."),
            Document(text="Sports news should show stadiums, sports equipment, or celebration imagery."),
            Document(text="Weather/disaster news requires relevant environmental imagery - rain, storms, clear skies."),
            Document(text="Cultural news works with festivals, traditional imagery, or community gatherings."),
            Document(text="Healthcare news should feature hospitals, medical equipment, or health-related imagery."),
            Document(text="Education news benefits from school/university buildings, students, or academic settings.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    def _build_media_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for media selection"""
        documents = [
            Document(text="YouTube Shorts require vertical 9:16 aspect ratio images that work well on mobile devices."),
            Document(text="News videos need professional, high-quality imagery that conveys credibility and authority."),
            Document(text="Each 8-10 second news segment should have 2-3 complementary images to maintain visual interest."),
            Document(text="Images should be copyright-free and safe for commercial use to avoid legal issues."),
            Document(text="Color schemes should be neutral and professional, avoiding overly bright or distracting colors."),
            Document(text="Text overlays require images with clear spaces for readable typography."),
            Document(text="Regional news benefits from location-specific imagery when available."),
            Document(text="Stock photography should look natural and not overly staged for news credibility."),
            Document(text="Image resolution should be minimum 1080x1920 for crisp video quality."),
            Document(text="Sequential images should have visual coherence and smooth transitions.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    async def _search_unsplash(self, query: str, count: int = 5) -> List[Dict]:
        """Search Unsplash for copyright-free images"""
        if not self.unsplash_key:
            logger.warning("Unsplash API key not configured")
            return []
        
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
            params = {
                "query": query,
                "per_page": count,
                "orientation": "portrait",  # For 9:16 aspect ratio
                "order_by": "relevant"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for photo in data.get("results", []):
                            results.append({
                                "id": photo["id"],
                                "url": photo["urls"]["regular"],
                                "download_url": photo["urls"]["full"],
                                "description": photo.get("alt_description", ""),
                                "source": "unsplash",
                                "attribution": f"Photo by {photo['user']['name']} on Unsplash"
                            })
                        
                        return results
                    else:
                        logger.error(f"Unsplash API error: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error searching Unsplash: {e}")
            return []
    
    async def _search_pexels(self, query: str, count: int = 5) -> List[Dict]:
        """Search Pexels for copyright-free images"""
        if not self.pexels_key:
            logger.warning("Pexels API key not configured")
            return []
        
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_key}
            params = {
                "query": query,
                "per_page": count,
                "orientation": "portrait",
                "size": "large"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for photo in data.get("photos", []):
                            results.append({
                                "id": photo["id"],
                                "url": photo["src"]["large"],
                                "download_url": photo["src"]["original"],
                                "description": photo.get("alt", ""),
                                "source": "pexels",
                                "attribution": f"Photo by {photo['photographer']} on Pexels"
                            })
                        
                        return results
                    else:
                        logger.error(f"Pexels API error: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error searching Pexels: {e}")
            return []
    
    async def _download_media(self, media_item: Dict, category: str) -> Optional[str]:
        """Download media file to local cache"""
        try:
            os.makedirs("./data/media_cache", exist_ok=True)
            
            file_extension = ".jpg"  # Default to jpg
            filename = f"{category}_{media_item['id']}{file_extension}"
            filepath = f"./data/media_cache/{filename}"
            
            # Check if already cached
            if os.path.exists(filepath):
                return filepath
            
            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(media_item['download_url']) as response:
                    if response.status == 200:
                        with open(filepath, 'wb') as f:
                            f.write(await response.read())
                        
                        logger.info(f"Downloaded media: {filepath}")
                        return filepath
                    else:
                        logger.error(f"Failed to download media: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error downloading media: {e}")
            return None
    
    def _generate_search_terms(self, content: str, category: str) -> List[str]:
        """Generate relevant search terms from content and category"""
        # Base terms by category
        category_terms = {
            "international": ["world news", "global", "international", "diplomacy"],
            "national": ["india", "government", "parliament", "delhi"],
            "karnataka": ["bangalore", "karnataka", "india tech", "silicon valley india"],
            "tamilnadu": ["chennai", "tamil nadu", "south india"],
            "andhra": ["hyderabad", "andhra pradesh", "telangana"],
            "kerala": ["kerala", "cochin", "backwaters"]
        }
        
        base_terms = category_terms.get(category, ["news", "india"])
        
        # Extract keywords from content
        content_words = content.lower().split()
        important_words = []
        
        # Look for key nouns and topics
        key_patterns = ["government", "minister", "election", "policy", "economy", 
                       "technology", "business", "education", "health", "sports"]
        
        for word in content_words:
            for pattern in key_patterns:
                if pattern in word:
                    important_words.append(pattern)
        
        # Combine base terms with content-derived terms
        search_terms = base_terms + important_words[:3]  # Limit to avoid too many terms
        
        return search_terms[:5]  # Return top 5 terms
    
    async def find_relevant_media(self, content: str, category: str) -> List[Dict]:
        """Find relevant media for news content"""
        try:
            # Use agent to analyze and find media
            prompt = f"""
            Find relevant visual media for {category} news content:
            
            Content: {content}
            Category: {category}
            
            Steps:
            1. Use visual_concept_mapper to identify key visual concepts
            2. Use media_selector to determine appropriate media types
            3. Generate search terms for stock photo APIs
            4. Search both Unsplash and Pexels for relevant images
            5. Select best 3-4 images for 8-10 second segment
            
            Focus on professional, copyright-free imagery suitable for news video.
            """
            
            response = await self.agent.achat(prompt)
            
            # Generate search terms
            search_terms = self._generate_search_terms(content, category)
            
            # Search multiple sources
            all_media = []
            
            for term in search_terms[:2]:  # Use top 2 search terms
                # Search Unsplash
                unsplash_results = await self._search_unsplash(term, 3)
                all_media.extend(unsplash_results)
                
                # Search Pexels
                pexels_results = await self._search_pexels(term, 3)
                all_media.extend(pexels_results)
            
            # Download and cache selected media
            selected_media = []
            for media_item in all_media[:4]:  # Select top 4 images
                local_path = await self._download_media(media_item, category)
                if local_path:
                    media_item['local_path'] = local_path
                    selected_media.append(media_item)
            
            logger.info(f"Found {len(selected_media)} media items for {category}")
            return selected_media
            
        except Exception as e:
            logger.error(f"Error finding media for {category}: {e}")
            # Return fallback media
            return [{
                "id": "fallback",
                "description": f"Fallback image for {category}",
                "source": "fallback",
                "local_path": None
            }]
    
    async def collect_media_batch(self, content_dict: Dict[str, str]) -> Dict[str, List[Dict]]:
        """Collect media for multiple news items"""
        media_collections = {}
        
        # Create tasks for concurrent execution
        tasks = []
        for category, content in content_dict.items():
            if content and content.strip():
                task = self.find_relevant_media(content, category)
                tasks.append((category, task))
        
        # Execute all tasks concurrently
        for category, task in tasks:
            try:
                media_items = await task
                media_collections[category] = media_items
            except Exception as e:
                logger.error(f"Failed to collect media for {category}: {e}")
                media_collections[category] = []
        
        return media_collections