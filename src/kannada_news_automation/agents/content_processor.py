from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.openai import OpenAI
# from llama_index.core.agent import ReActAgent  # Disabled for compatibility
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from typing import Dict, List
import logging
import re

logger = logging.getLogger(__name__)

class ContentProcessingAgent:
    def __init__(self):
        """Initialize content processing agent with video-optimized summarization"""
        self.llm = OpenAI(model="gpt-4")
        self.summarization_kb = self._build_summarization_knowledge_base()
        self.video_kb = self._build_video_knowledge_base()
        
        # Create query engines
        self.summary_engine = self.summarization_kb.as_query_engine()
        self.video_engine = self.video_kb.as_query_engine()
        
        # Create tools
        self.tools = [
            QueryEngineTool(
                query_engine=self.summary_engine,
                metadata=ToolMetadata(
                    name="summarization_optimizer",
                    description="Optimizes content summarization for video format"
                )
            ),
            QueryEngineTool(
                query_engine=self.video_engine,
                metadata=ToolMetadata(
                    name="video_formatter",
                    description="Formats content for video presentation"
                )
            ),
            FunctionTool.from_defaults(fn=self._extract_key_points),
            FunctionTool.from_defaults(fn=self._optimize_for_audio),
            FunctionTool.from_defaults(fn=self._calculate_reading_time)
        ]
        
        # Use simple query engine instead of agent for now
        self.query_engine = self.summarization_kb.as_query_engine(llm=self.llm)
    
    def _build_summarization_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for content summarization techniques"""
        documents = [
            Document(text="Effective news summaries start with the most important information (Who, What, When, Where, Why)."),
            Document(text="For video content, each sentence should be concise and impactful, avoiding complex subordinate clauses."),
            Document(text="Political news summaries should focus on policy impact and public consequences rather than process details."),
            Document(text="Economic news should translate complex data into simple terms that common people can understand."),
            Document(text="Regional news summaries should emphasize local impact and community relevance."),
            Document(text="International news for Indian audience should connect to domestic implications and relevance."),
            Document(text="Sports news should capture the excitement and key moments without excessive technical details."),
            Document(text="Breaking news summaries need urgency markers and clear factual statements.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    def _build_video_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for video content optimization"""
        documents = [
            Document(text="Video content should be structured in short, digestible segments of 8-12 words per sentence."),
            Document(text="Each news segment in a 60-second video should be 8-10 seconds for optimal pacing."),
            Document(text="Transitions between news items should be smooth with connecting phrases like 'Meanwhile' or 'In other news'."),
            Document(text="Numbers and statistics should be presented clearly with context for better audio comprehension."),
            Document(text="Names of people and places should be phonetically clear for text-to-speech systems."),
            Document(text="Video scripts should avoid abbreviations and use full forms for better speech synthesis."),
            Document(text="Content should maintain journalistic neutrality while being engaging for mobile viewers."),
            Document(text="Each summary should end with a clear conclusion or impact statement.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    def _extract_key_points(self, text: str, max_points: int = 3) -> List[str]:
        """Extract key points from news content"""
        # Simple extraction based on sentence importance
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Score sentences based on keywords
        important_words = ['said', 'announced', 'revealed', 'confirmed', 'reported', 'decided']
        scored_sentences = []
        
        for sentence in sentences:
            score = 0
            words = sentence.lower().split()
            
            # Score based on important words
            for word in important_words:
                if word in words:
                    score += 1
            
            # Score based on sentence position (earlier sentences are more important)
            position_bonus = (len(sentences) - sentences.index(sentence)) / len(sentences)
            score += position_bonus
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and return top points
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, score in scored_sentences[:max_points]]
    
    def _optimize_for_audio(self, text: str) -> str:
        """Optimize text for audio delivery"""
        # Replace problematic characters and abbreviations
        optimized = text.replace('&', 'and')
        optimized = re.sub(r'\b(Dr|Mr|Mrs|Ms)\b', lambda m: m.group().replace('.', ''), optimized)
        optimized = re.sub(r'\b(\d+)%', r'\1 percent', optimized)
        optimized = re.sub(r'\$(\d+)', r'\1 dollars', optimized)
        optimized = re.sub(r'₹(\d+)', r'\1 rupees', optimized)
        
        # Add pauses for better pacing
        optimized = optimized.replace(',', ', ')
        optimized = optimized.replace(':', ': ')
        
        # Clean up multiple spaces
        optimized = re.sub(r'\s+', ' ', optimized)
        
        return optimized.strip()
    
    def _calculate_reading_time(self, text: str, words_per_minute: int = 150) -> float:
        """Calculate estimated reading/speaking time"""
        word_count = len(text.split())
        return (word_count / words_per_minute) * 60  # Return seconds
    
    async def create_video_summary(self, content: str, category: str, target_duration: float = 10.0) -> str:
        """Create optimized summary for video content"""
        try:
            prompt = f"""
            Create a video-optimized summary for {category} news content:
            
            Original content: {content}
            Target duration: {target_duration} seconds
            Target word count: {int(target_duration * 2.5)} words (150 words per minute speech rate)
            
            Requirements:
            1. Use summarization_optimizer to create engaging, concise summary
            2. Use video_formatter to optimize for video presentation
            3. Extract key points and organize them logically
            4. Optimize text for audio delivery (clear pronunciation, proper pacing)
            5. Ensure reading time matches target duration
            
            Focus on:
            - Clear, simple sentences
            - Important facts first
            - Engaging language for Kannada-speaking audience
            - Smooth flow for video narration
            """
            
            response = await self.agent.achat(prompt)
            
            # Extract key points and create structured summary
            key_points = self._extract_key_points(content)
            
            # Create summary based on category and key points
            if category in ['karnataka', 'tamilnadu', 'andhra', 'kerala']:
                summary_prefix = f"In {category.capitalize()}, "
            elif category == 'national':
                summary_prefix = "Across India, "
            else:
                summary_prefix = "In international news, "
            
            # Combine key points into flowing narrative
            if key_points:
                main_summary = ". ".join(key_points[:2])  # Use top 2 key points
                final_summary = summary_prefix + main_summary
            else:
                # Fallback to first 100 words of content
                words = content.split()[:25]  # ~10 seconds of speech
                final_summary = summary_prefix + " ".join(words)
            
            # Optimize for audio
            final_summary = self._optimize_for_audio(final_summary)
            
            # Check duration and adjust if needed
            estimated_time = self._calculate_reading_time(final_summary)
            if estimated_time > target_duration * 1.2:  # 20% tolerance
                # Truncate if too long
                words = final_summary.split()
                target_words = int(target_duration * 2.5)  # 150 wpm = 2.5 wps
                final_summary = " ".join(words[:target_words]) + "."
            
            logger.info(f"Created summary for {category}: {len(final_summary.split())} words, ~{self._calculate_reading_time(final_summary):.1f}s")
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Error creating video summary for {category}: {e}")
            # Fallback summary
            words = content.split()[:25]
            return f"In {category} news, " + " ".join(words) + "."
    
    async def process_batch_content(self, news_data: Dict[str, Dict]) -> Dict[str, str]:
        """Process multiple news items for video format"""
        # Define time allocation for each category
        time_allocation = {
            "international": 8,
            "national": 8,
            "karnataka": 10,  # Priority for regional audience
            "tamilnadu": 8,
            "andhra": 8,
            "kerala": 8
        }
        
        processed_content = {}
        
        for category, news_item in news_data.items():
            if news_item and news_item.get('content'):
                target_time = time_allocation.get(category, 8)
                summary = await self.create_video_summary(
                    news_item['content'], 
                    category, 
                    target_time
                )
                processed_content[category] = summary
            else:
                logger.warning(f"No content found for category: {category}")
        
        return processed_content