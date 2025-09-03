from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.openai import OpenAI
# from llama_index.core.agent import ReActAgent  # Disabled for compatibility
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from typing import Dict, List
import logging
import re

logger = logging.getLogger(__name__)

class TranslationAgent:
    def __init__(self):
        """Initialize translation agent with cultural context awareness"""
        self.llm = OpenAI(model="gpt-4")
        self.cultural_kb = self._build_cultural_knowledge_base()
        self.linguistic_kb = self._build_linguistic_knowledge_base()
        
        # Create query engines
        self.cultural_engine = self.cultural_kb.as_query_engine()
        self.linguistic_engine = self.linguistic_kb.as_query_engine()
        
        # Create tools
        self.tools = [
            QueryEngineTool(
                query_engine=self.cultural_engine,
                metadata=ToolMetadata(
                    name="cultural_adapter",
                    description="Adapts content with cultural context for Kannada audience"
                )
            ),
            QueryEngineTool(
                query_engine=self.linguistic_engine,
                metadata=ToolMetadata(
                    name="linguistic_optimizer",
                    description="Optimizes Kannada translation for natural speech"
                )
            ),
            FunctionTool.from_defaults(fn=self._handle_proper_nouns),
            FunctionTool.from_defaults(fn=self._optimize_for_tts),
            FunctionTool.from_defaults(fn=self._validate_translation)
        ]
        
        # Use simple query engines instead of agent for now
        # Already created above: self.cultural_engine and self.linguistic_engine
    
    def _build_cultural_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for cultural context"""
        documents = [
            Document(text="Karnataka audience prefers news that connects to local governance, Bangalore development, and state politics."),
            Document(text="Economic news should relate to IT industry, agriculture, and small business impact in Karnataka."),
            Document(text="International news should emphasize connections to Indian diaspora and technology sector."),
            Document(text="Political translations should use respectful terms for leaders and neutral language for controversial topics."),
            Document(text="Regional pride is important - highlight Karnataka's achievements and contributions when relevant."),
            Document(text="Cultural references should be familiar to South Indian context - festivals, traditions, local customs."),
            Document(text="Numbers and statistics should use Indian numbering system (lakhs, crores) when appropriate."),
            Document(text="Geographic references should include both English and local names when first mentioned."),
            Document(text="Religious and cultural sensitivities must be maintained in translations."),
            Document(text="Contemporary Kannada should be used - avoid overly classical or archaic terms.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    def _build_linguistic_knowledge_base(self) -> VectorStoreIndex:
        """Build knowledge base for linguistic optimization"""
        documents = [
            Document(text="Kannada TTS works best with clear consonant clusters and proper vowel pronunciation patterns."),
            Document(text="Sanskrit loanwords in Kannada should maintain traditional pronunciation for TTS accuracy."),
            Document(text="English proper nouns can be transliterated or kept in English based on familiarity."),
            Document(text="News terminology has established Kannada equivalents that should be used consistently."),
            Document(text="Sentence structure should follow natural Kannada SOV (Subject-Object-Verb) order."),
            Document(text="Compound words should be properly segmented for TTS pronunciation."),
            Document(text="Technical terms should be explained or accompanied by English equivalents in parentheses."),
            Document(text="Quotations and dialogue should use appropriate Kannada speech markers."),
            Document(text="Time references should use standard Kannada temporal expressions."),
            Document(text="Formal news register should be maintained while keeping language accessible.")
        ]
        return VectorStoreIndex.from_documents(documents)
    
    def _handle_proper_nouns(self, text: str) -> str:
        """Handle proper nouns for better pronunciation"""
        # Common proper noun patterns
        proper_noun_map = {
            "Karnataka": "ಕರ್ನಾಟಕ",
            "Bangalore": "ಬೆಂಗಳೂರು",
            "Bengaluru": "ಬೆಂಗಳೂರು",
            "Mysore": "ಮೈಸೂರು",
            "Tamil Nadu": "ತಮಿಳುನಾಡು",
            "Kerala": "ಕೇರಳ",
            "Andhra Pradesh": "ಆಂಧ್ರ ಪ್ರದೇಶ",
            "India": "ಭಾರತ",
            "Prime Minister": "ಪ್ರಧಾನಮಂತ್ರಿ",
            "Chief Minister": "ಮುಖ್ಯಮಂತ್ರಿ",
            "Government": "ಸರ್ಕಾರ",
            "Parliament": "ಸಂಸತ್ತು"
        }
        
        # Replace common terms
        for english, kannada in proper_noun_map.items():
            text = text.replace(english, kannada)
        
        return text
    
    def _optimize_for_tts(self, text: str) -> str:
        """Optimize Kannada text for TTS pronunciation"""
        # Add pronunciation guides for complex words
        optimized = text
        
        # Handle common TTS problematic patterns
        optimized = re.sub(r'(\d+)', r' \1 ', optimized)  # Add spaces around numbers
        optimized = re.sub(r'([.!?])', r'\1 ', optimized)  # Add space after punctuation
        optimized = re.sub(r'\s+', ' ', optimized)  # Clean multiple spaces
        
        # Handle Sanskrit/English hybrid words
        optimized = optimized.replace('ಟೆಕ್ನಾಲಜಿ', 'ತಂತ್ರಜ್ಞಾನ')
        optimized = optimized.replace('ಗವರ್ನ್ಮೆಂಟ್', 'ಸರ್ಕಾರ')
        
        return optimized.strip()
    
    def _validate_translation(self, translation: str) -> bool:
        """Basic validation of Kannada translation"""
        # Check for Kannada script
        kannada_chars = len([c for c in translation if '\u0c80' <= c <= '\u0cff'])
        total_chars = len([c for c in translation if c.isalpha()])
        
        if total_chars == 0:
            return False
        
        # At least 70% should be Kannada characters
        kannada_percentage = kannada_chars / total_chars
        return kannada_percentage >= 0.7
    
    async def translate_with_context(self, text: str, category: str) -> str:
        """Translate English text to Kannada with cultural context"""
        try:
            prompt = f"""
            Translate the following English news text to natural, fluent Kannada with cultural context:
            
            Text: {text}
            Category: {category}
            
            Requirements:
            1. Use cultural_adapter to ensure cultural appropriateness for Kannada-speaking audience
            2. Use linguistic_optimizer to create natural-sounding Kannada for TTS
            3. Handle proper nouns appropriately (transliterate or keep English based on familiarity)
            4. Optimize text for text-to-speech pronunciation
            5. Maintain journalistic tone while being accessible
            6. Use contemporary Kannada that sounds natural when spoken
            
            Focus on:
            - Natural sentence flow in Kannada
            - Appropriate cultural references
            - Clear pronunciation for TTS
            - Professional news language
            - Local relevance for {category} news
            """
            
            response = await self.agent.achat(prompt)
            
            # Direct translation using GPT-4 with context
            translation_prompt = f"""
            Translate this English news text to natural, fluent Kannada suitable for news broadcast:
            
            "{text}"
            
            Guidelines:
            - Use contemporary Kannada that sounds natural when spoken
            - Maintain professional news tone
            - Keep proper nouns in English if commonly known (like "Karnataka", "India")
            - Use standard Kannada equivalents for political and administrative terms
            - Ensure smooth sentence flow for audio delivery
            - Category context: {category}
            
            Provide only the Kannada translation:
            """
            
            translation = await self.llm.acomplete(translation_prompt)
            kannada_text = translation.text.strip()
            
            # Handle proper nouns
            kannada_text = self._handle_proper_nouns(kannada_text)
            
            # Optimize for TTS
            kannada_text = self._optimize_for_tts(kannada_text)
            
            # Validate translation
            if not self._validate_translation(kannada_text):
                logger.warning(f"Translation validation failed for {category}")
                # Fallback to simpler translation
                simple_prompt = f"Translate to Kannada: {text}"
                fallback = await self.llm.acomplete(simple_prompt)
                kannada_text = fallback.text.strip()
            
            logger.info(f"Translated {category} content to Kannada: {len(kannada_text)} characters")
            return kannada_text
            
        except Exception as e:
            logger.error(f"Error translating {category} content: {e}")
            # Emergency fallback
            return f"ಸುದ್ದಿ: {text[:100]}..."  # "News: [text]..."
    
    async def translate_batch(self, content_dict: Dict[str, str]) -> Dict[str, str]:
        """Translate multiple content items to Kannada"""
        translations = {}
        
        for category, text in content_dict.items():
            if text and text.strip():
                translation = await self.translate_with_context(text, category)
                translations[category] = translation
            else:
                logger.warning(f"No text to translate for category: {category}")
                translations[category] = ""
        
        return translations
    
    def create_category_intro(self, category: str) -> str:
        """Create category introduction in Kannada"""
        intros = {
            "international": "ಅಂತರರಾಷ್ಟ್ರೀಯ ಸುದ್ದಿಯಲ್ಲಿ,",
            "national": "ರಾಷ್ಟ್ರೀಯ ಸುದ್ದಿಯಲ್ಲಿ,",
            "karnataka": "ಕರ್ನಾಟಕದಲ್ಲಿ,",
            "tamilnadu": "ತಮಿಳುನಾಡಿನಲ್ಲಿ,",
            "andhra": "ಆಂಧ್ರ ಪ್ರದೇಶದಲ್ಲಿ,",
            "kerala": "ಕೇರಳದಲ್ಲಿ,"
        }
        return intros.get(category, "ಸುದ್ದಿಯಲ್ಲಿ,")