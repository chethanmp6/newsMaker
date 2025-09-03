from llama_index.core import VectorStoreIndex, Document, ServiceContext
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
import asyncio
import aiohttp
import feedparser
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class NewsCollectionAgent:
    def __init__(self):
        """Initialize news collection agent with LlamaIndex RAG capabilities"""
        self.llm = OpenAI(model="gpt-4")
        self.trending_kb = self._build_trending_knowledge_base()
        self.regional_kb = self._build_regional_knowledge_base()
        
        # Create query engines
        self.trending_engine = self.trending_kb.as_query_engine()
        self.regional_engine = self.regional_kb.as_query_engine()
        
        # Define news sources
        self.news_sources = {
            "international": [
                "https://feeds.bbci.co.uk/news/world/rss.xml",
                "https://rss.cnn.com/rss/edition.rss"
            ],
            "national": [
                "https://www.thehindu.com/news/national/feeder/default.rss",
                "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
            ],
            "karnataka": [
                "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
                "https://www.deccanherald.com/rss/state.rss"
            ],
            "tamilnadu": [
                "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss"
            ],
            "andhra": [
                "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss"
            ],
            "kerala": [
                "https://www.thehindu.com/news/national/kerala/feeder/default.rss"
            ]
        }
        
        # Create tools for the agent
        self.tools = [
            QueryEngineTool(
                query_engine=self.trending_engine,
                metadata=ToolMetadata(
                    name="trending_analyzer",
                    description="Analyzes if news is trending based on patterns"
                )
            ),
            QueryEngineTool(
                query_engine=self.regional_engine,
                metadata=ToolMetadata(
                    name="regional_filter", 
                    description="Filters news based on regional relevance"
                )
            ),
            FunctionTool.from_defaults(fn=self._fetch_rss_news),
            FunctionTool.from_defaults(fn=self._analyze_engagement)
        ]
        
        # Use simple query engine instead of agent for now
        self.query_engine = self.trending_kb.as_query_engine(llm=self.llm)
    
    def _build_trending_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for trending news patterns"""
        documents = [
            Document(text="News becomes trending when it has high social media engagement, multiple source coverage, and rapid spread across platforms within 6 hours."),
            Document(text="Political news trends differently - requires controversy, policy impact, or election relevance."),
            Document(text="Sports news peaks during match times and major tournaments."),
            Document(text="Economic news trends when it affects common people - inflation, fuel prices, job market."),
            Document(text="Entertainment news needs celebrity involvement or cultural significance."),
            Document(text="Regional news trends when it impacts local communities or has state-wide implications.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    def _build_regional_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for regional news relevance"""
        documents = [
            Document(text="Karnataka news should focus on Bangalore tech industry, regional politics, cultural events, and development projects."),
            Document(text="Tamil Nadu news interests include Chennai industries, Tamil cinema, regional politics, and educational institutions."),
            Document(text="Andhra Pradesh news covers Hyderabad tech sector, state bifurcation issues, and agricultural policies."),
            Document(text="Kerala news includes maritime trade, tourism, agricultural issues, and Gulf migration topics."),
            Document(text="National news relevant to South India: central policies affecting states, inter-state disputes, infrastructure projects."),
            Document(text="International news relevant to South Indians: IT industry impacts, Gulf country policies, education opportunities.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    async def _fetch_rss_news(self, sources: List[str]) -> List[Dict]:
        """Fetch news from RSS feeds"""
        all_news = []
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    async with session.get(source) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:10]:  # Latest 10 from each source
                                news_item = {
                                    'title': entry.title,
                                    'summary': entry.get('summary', ''),
                                    'link': entry.link,
                                    'published': entry.get('published', ''),
                                    'source': source
                                }
                                all_news.append(news_item)
                except Exception as e:
                    logger.error(f"Error fetching from {source}: {e}")
                    continue
        return all_news
    
    def _analyze_engagement(self, news_items: List[Dict]) -> List[Dict]:
        """Analyze engagement potential of news items"""
        # Simple engagement scoring based on title keywords and recency
        engagement_keywords = {
            'high': ['breaking', 'urgent', 'exclusive', 'scandal', 'victory', 'defeat'],
            'medium': ['announces', 'launches', 'opens', 'closes', 'wins', 'loses'],
            'low': ['meeting', 'discussion', 'routine', 'regular', 'annual']
        }
        
        for item in news_items:
            score = 0.5  # baseline
            title_lower = item['title'].lower()
            
            for keyword in engagement_keywords['high']:
                if keyword in title_lower:
                    score += 0.3
            
            for keyword in engagement_keywords['medium']:
                if keyword in title_lower:
                    score += 0.2
                    
            for keyword in engagement_keywords['low']:
                if keyword in title_lower:
                    score -= 0.1
            
            item['engagement_score'] = min(1.0, max(0.1, score))
        
        return sorted(news_items, key=lambda x: x['engagement_score'], reverse=True)
    
    async def collect_trending_news(self, category: str) -> Dict:
        """Collect top trending news for a category"""
        try:
            # Get news sources for category
            sources = self.news_sources.get(category, [])
            if not sources:
                logger.error(f"No sources found for category: {category}")
                return {}
            
            # Use agent to collect and analyze news
            prompt = f"""
            Collect trending news for category '{category}' from the available sources.
            
            Steps:
            1. Fetch news from RSS feeds for this category
            2. Use trending_analyzer to verify which news items are actually trending
            3. Use regional_filter to ensure regional relevance for {category}
            4. Analyze engagement potential of each news item
            5. Return the single most relevant trending news item
            
            Focus on news that would interest Kannada-speaking South Indian audience.
            Ensure the selected news is recent (within last 24 hours) and has high engagement potential.
            """
            
            response = await self.agent.achat(prompt)
            
            # Extract the actual news data (this would need proper parsing in real implementation)
            news_data = await self._fetch_rss_news(sources)
            analyzed_news = self._analyze_engagement(news_data)
            
            if analyzed_news:
                top_news = analyzed_news[0]
                return {
                    'category': category,
                    'title': top_news['title'],
                    'content': top_news['summary'],
                    'url': top_news['link'],
                    'engagement_score': top_news['engagement_score'],
                    'source': top_news['source'],
                    'analysis': response.response
                }
            else:
                logger.warning(f"No news found for category: {category}")
                return {}
                
        except Exception as e:
            logger.error(f"Error collecting news for {category}: {e}")
            return {}
    
    async def collect_all_categories(self) -> Dict[str, Dict]:
        """Collect trending news for all categories"""
        categories = ["international", "national", "karnataka", "tamilnadu", "andhra", "kerala"]
        
        tasks = [self.collect_trending_news(category) for category in categories]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        collected_news = {}
        for category, result in zip(categories, results):
            if isinstance(result, Exception):
                logger.error(f"Exception for {category}: {result}")
                collected_news[category] = {}
            else:
                collected_news[category] = result
        
        return collected_news