"""
Style Analyzer - Extracts and quantifies writing patterns and voice characteristics
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import Counter
import statistics

@dataclass
class StyleMetrics:
    """Quantified writing style characteristics"""
    avg_sentence_length: float
    paragraph_length: float
    punctuation_patterns: Dict[str, float]
    vocabulary_complexity: float
    tone_indicators: Dict[str, int]
    structural_patterns: Dict[str, int]
    confidence_score: float

class StyleAnalyzer:
    """Analyzes and quantifies writing style patterns"""
    
    def __init__(self):
        # Paul Golding's known style patterns
        self.golding_patterns = {
            "double_dash": r"--",
            "technical_depth": r"(architecture|framework|implementation|system|protocol)",
            "future_vision": r"(will|future|next|evolution|transform|enable)",
            "structured_thinking": r"(first|second|third|therefore|however|moreover)",
            "industry_terms": r"(enterprise|scale|ecosystem|integration|deployment)"
        }
        
        # Keshav's style patterns  
        self.keshav_patterns = {
            "authenticity": r"(actually|honestly|genuinely|truly)",
            "metrics_driven": r"(\d+%|\d+x|\d+K|\d+M|€\d+)",
            "story_elements": r"(journey|story|experience|challenge|achievement)",
            "enthusiasm": r"(amazing|incredible|exciting|fantastic|love)",
            "future_focused": r"(vision|future|next|building|creating)"
        }
    
    def analyze_text(self, text: str) -> StyleMetrics:
        """Comprehensive style analysis of input text"""
        
        sentences = self._split_sentences(text)
        paragraphs = self._split_paragraphs(text)
        
        return StyleMetrics(
            avg_sentence_length=self._calculate_avg_sentence_length(sentences),
            paragraph_length=self._calculate_avg_paragraph_length(paragraphs),
            punctuation_patterns=self._analyze_punctuation(text),
            vocabulary_complexity=self._calculate_vocabulary_complexity(text),
            tone_indicators=self._extract_tone_indicators(text),
            structural_patterns=self._analyze_structure(text),
            confidence_score=0.85
        )
    
    def extract_golding_voice_features(self, text: str) -> Dict[str, Any]:
        """Extract Paul Golding's specific voice characteristics"""
        
        features = {
            "double_dash_usage": len(re.findall(self.golding_patterns["double_dash"], text)),
            "technical_depth_score": len(re.findall(self.golding_patterns["technical_depth"], text, re.I)),
            "future_vision_indicators": len(re.findall(self.golding_patterns["future_vision"], text, re.I)),
            "structured_approach": len(re.findall(self.golding_patterns["structured_thinking"], text, re.I)),
            "industry_terminology": len(re.findall(self.golding_patterns["industry_terms"], text, re.I)),
        }
        
        # Calculate voice signature strength
        total_indicators = sum(features.values())
        text_length = len(text.split())
        features["voice_strength"] = (total_indicators / text_length) * 100 if text_length > 0 else 0
        
        return features
    
    def extract_keshav_voice_features(self, text: str) -> Dict[str, Any]:
        """Extract Keshav's specific voice characteristics"""
        
        features = {
            "authenticity_markers": len(re.findall(self.keshav_patterns["authenticity"], text, re.I)),
            "metrics_integration": len(re.findall(self.keshav_patterns["metrics_driven"], text)),
            "storytelling_elements": len(re.findall(self.keshav_patterns["story_elements"], text, re.I)),
            "enthusiasm_level": len(re.findall(self.keshav_patterns["enthusiasm"], text, re.I)),
            "future_orientation": len(re.findall(self.keshav_patterns["future_focused"], text, re.I)),
        }
        
        # Calculate authenticity score
        text_length = len(text.split())
        features["authenticity_score"] = (features["authenticity_markers"] + features["storytelling_elements"]) / text_length * 100 if text_length > 0 else 0
        
        return features
    
    def generate_style_prompt(self, target_voice: str, context: str = "") -> str:
        """Generate prompt for style-specific content generation"""
        
        if target_voice.lower() == "paul_golding":
            return f"""
            Write in Paul Golding's distinctive voice and style:
            
            VOICE CHARACTERISTICS:
            - Use double dashes (--) for emphasis and clarification
            - Demonstrate deep technical understanding with specific terminology
            - Show structured, logical thinking progression
            - Include forward-looking vision and industry insights
            - Maintain executive-level professionalism with accessibility
            - Balance technical depth with strategic overview
            
            TONE: Professional, visionary, technically grounded
            STRUCTURE: Clear logical flow with supporting details
            CONTEXT: {context}
            """
            
        elif target_voice.lower() == "keshav":
            return f"""
            Write in Keshav Joglekar's authentic voice:
            
            VOICE CHARACTERISTICS:
            - Use authentic enthusiasm markers ("actually", "honestly")
            - Integrate specific metrics and quantified achievements naturally
            - Include story-driven elements and personal journey
            - Show genuine passion for AI and technology impact
            - Balance technical depth with accessible explanations
            - Demonstrate results-oriented thinking
            
            TONE: Enthusiastic, authentic, metrics-driven, future-focused
            STRUCTURE: Story-driven with supporting data points
            CONTEXT: {context}
            """
        
        return f"Write professionally about: {context}"
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        return re.split(r'[.!?]+', text.strip())
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _calculate_avg_sentence_length(self, sentences: List[str]) -> float:
        """Calculate average sentence length in words"""
        if not sentences:
            return 0.0
        lengths = [len(s.split()) for s in sentences if s.strip()]
        return statistics.mean(lengths) if lengths else 0.0
    
    def _calculate_avg_paragraph_length(self, paragraphs: List[str]) -> float:
        """Calculate average paragraph length in sentences"""
        if not paragraphs:
            return 0.0
        lengths = [len(self._split_sentences(p)) for p in paragraphs]
        return statistics.mean(lengths) if lengths else 0.0
    
    def _analyze_punctuation(self, text: str) -> Dict[str, float]:
        """Analyze punctuation usage patterns"""
        total_chars = len(text)
        if total_chars == 0:
            return {}
        
        return {
            "period_density": text.count('.') / total_chars * 100,
            "comma_density": text.count(',') / total_chars * 100,
            "exclamation_density": text.count('!') / total_chars * 100,
            "question_density": text.count('?') / total_chars * 100,
            "dash_density": text.count('--') / total_chars * 100,
        }
    
    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """Calculate vocabulary complexity score"""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        unique_words = set(words)
        return len(unique_words) / len(words)  # Type-token ratio
    
    def _extract_tone_indicators(self, text: str) -> Dict[str, int]:
        """Extract words that indicate tone"""
        positive_words = r'\b(excellent|great|amazing|fantastic|love|excited|thrilled)\b'
        technical_words = r'\b(architecture|system|framework|implementation|protocol)\b'
        future_words = r'\b(will|future|next|vision|transform|evolve)\b'
        
        return {
            "positive": len(re.findall(positive_words, text, re.I)),
            "technical": len(re.findall(technical_words, text, re.I)),
            "future": len(re.findall(future_words, text, re.I))
        }
    
    def _analyze_structure(self, text: str) -> Dict[str, int]:
        """Analyze structural elements"""
        return {
            "paragraphs": len(self._split_paragraphs(text)),
            "sentences": len([s for s in self._split_sentences(text) if s.strip()]),
            "bullet_points": text.count('•') + text.count('-') + text.count('*'),
            "numbers": len(re.findall(r'\d+', text))
        }

# Global analyzer instance
style_analyzer = StyleAnalyzer()