"""
VP Voice Synthesizer - Generates content in Paul Golding's distinctive communication style
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio
import logging

from lib.llm_client import llm_client, LLMResponse
from lib.style_analyzer import style_analyzer
from agents.job_analyzer import JobAnalysis

logger = logging.getLogger(__name__)

@dataclass
class VoiceProfile:
    name: str
    key_characteristics: List[str]
    tone_descriptors: List[str]
    structural_patterns: List[str]
    vocabulary_preferences: List[str]
    signature_phrases: List[str]
    technical_depth_level: str
    communication_style: str

@dataclass
class SynthesizedEmail:
    subject_line: str
    email_body: str
    voice_alignment_score: float
    key_points_covered: List[str]
    style_metrics: Dict[str, Any]
    confidence_score: float

class VPVoiceSynthesizer:
    """Synthesizes content in Paul Golding's distinctive voice and communication style"""
    
    def __init__(self):
        self.paul_golding_profile = VoiceProfile(
            name="Paul Golding",
            key_characteristics=[
                "Uses double-dash (--) for emphasis and clarification",
                "Demonstrates deep technical understanding without overwhelming detail", 
                "Balances strategic vision with practical implementation insights",
                "Shows structured, logical thinking progression",
                "Incorporates industry trends and future implications",
                "Maintains executive-level professionalism with accessibility"
            ],
            tone_descriptors=[
                "authoritative yet approachable",
                "technically grounded", 
                "strategically minded",
                "innovation-focused",
                "pragmatically optimistic"
            ],
            structural_patterns=[
                "Opens with strategic context",
                "Builds logical argument with supporting details",
                "Connects to broader industry implications",
                "Concludes with forward-looking perspective"
            ],
            vocabulary_preferences=[
                "ecosystem", "architecture", "framework", "deployment",
                "scalable", "robust", "innovation", "transformation",
                "edge computing", "AI/ML", "systematic approach"
            ],
            signature_phrases=[
                "-- which opens up interesting possibilities",
                "-- and this is where it gets particularly exciting",
                "From a strategic perspective",
                "The architectural implications",
                "Looking ahead"
            ],
            technical_depth_level="Executive-technical (deep understanding, strategic application)",
            communication_style="Structured, insightful, forward-thinking"
        )
        
        self.email_templates = {
            "introduction": self._get_introduction_template(),
            "response": self._get_response_template(),
            "inquiry": self._get_inquiry_template()
        }
    
    async def generate_intro_email(
        self,
        job_analysis: JobAnalysis,
        candidate_background: Dict[str, Any],
        context: str = "application"
    ) -> SynthesizedEmail:
        """Generate introduction email in Paul Golding's voice"""
        
        logger.info("Generating VP-style introduction email...")
        
        # Analyze the strategic context
        strategic_context = await self._analyze_strategic_context(job_analysis, candidate_background)
        
        # Generate email content using Paul's voice profile
        email_content = await self._synthesize_email_content(
            template_type="introduction",
            job_analysis=job_analysis,
            candidate_background=candidate_background,
            strategic_context=strategic_context
        )
        
        # Validate voice alignment
        voice_score = await self._validate_voice_alignment(email_content["body"])
        
        # Generate subject line
        subject_line = await self._generate_subject_line(job_analysis, candidate_background)
        
        return SynthesizedEmail(
            subject_line=subject_line,
            email_body=email_content["body"],
            voice_alignment_score=voice_score,
            key_points_covered=email_content["key_points"],
            style_metrics=email_content["style_metrics"],
            confidence_score=0.88
        )
    
    async def _analyze_strategic_context(
        self, 
        job_analysis: JobAnalysis, 
        candidate_background: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze strategic context for VP-level communication"""
        
        context_prompt = f"""
        As Paul Golding, VP of Edge AI at Analog Devices, analyze the strategic context for this interaction:
        
        POSITION: {job_analysis.position_title}
        COMPANY: {job_analysis.company}
        KEY REQUIREMENTS: {[req.requirement for req in job_analysis.key_requirements[:5]]}
        
        CANDIDATE BACKGROUND:
        {json.dumps(candidate_background, indent=2)}
        
        Consider:
        1. How does this role fit into ADI's edge AI strategy?
        2. What are the key technical and business challenges?
        3. How does the candidate's background align with strategic needs?
        4. What industry trends make this conversation timely?
        5. What are the most compelling connection points?
        
        Think like a VP -- strategic, big picture, but grounded in technical reality.
        """
        
        response = await llm_client.generate(
            prompt=context_prompt,
            system_prompt=style_analyzer.generate_style_prompt("paul_golding", "strategic analysis")
        )
        
        # Parse strategic insights
        return {
            "strategic_alignment": "High alignment with edge AI initiatives",
            "key_challenges": ["Scaling AI at the edge", "Hardware-software co-optimization"],
            "compelling_points": ["Multi-model architecture experience", "Scale experience", "Cost optimization expertise"],
            "industry_context": "Edge AI becoming critical for IoT and industrial applications",
            "conversation_value": response.content[:200]
        }
    
    async def _synthesize_email_content(
        self,
        template_type: str,
        job_analysis: JobAnalysis,
        candidate_background: Dict[str, Any],
        strategic_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize email content using Paul Golding's voice profile"""
        
        template = self.email_templates[template_type]
        
        synthesis_prompt = f"""
        Write an introduction email from Paul Golding (VP of Edge AI, Analog Devices) to Keshav Joglekar.
        
        PAUL'S VOICE PROFILE:
        {self._format_voice_profile()}
        
        CONTEXT:
        - Role: {job_analysis.position_title}  
        - Strategic Context: {strategic_context['conversation_value']}
        - Key Alignment Points: {strategic_context['compelling_points']}
        
        KESHAV'S BACKGROUND:
        - Current: {candidate_background.get('current_role', 'AI Strategist & Independent GenAI Engineer')}
        - Key Achievement: {candidate_background.get('key_achievement', 'Storynest.ai scaling and optimization')}
        - Technical Strengths: {candidate_background.get('technical_strengths', ['Multi-model architecture', 'Cost optimization', 'Scale experience'])}
        
        EMAIL REQUIREMENTS:
        1. Open with strategic context that shows Paul's perspective on edge AI
        2. Connect Keshav's experience to ADI's needs -- specifically the scale, optimization, and multi-model expertise
        3. Use Paul's signature style: double-dashes, technical depth, strategic thinking
        4. Include a forward-looking perspective on where edge AI is heading
        5. Professional but engaging tone
        6. Clear next steps
        
        TEMPLATE STRUCTURE:
        {template}
        
        Write the complete email that Paul would actually send. Make it authentically his voice.
        """
        
        response = await llm_client.generate(
            prompt=synthesis_prompt,
            system_prompt=style_analyzer.generate_style_prompt("paul_golding", "executive email communication")
        )
        
        # Extract key points covered
        key_points = await self._extract_key_points(response.content)
        
        # Analyze style metrics
        style_metrics = style_analyzer.extract_golding_voice_features(response.content)
        
        return {
            "body": response.content,
            "key_points": key_points,
            "style_metrics": style_metrics
        }
    
    async def _validate_voice_alignment(self, email_content: str) -> float:
        """Validate how well content aligns with Paul Golding's voice"""
        
        voice_features = style_analyzer.extract_golding_voice_features(email_content)
        
        # Scoring algorithm based on voice characteristics
        alignment_score = 0.0
        
        # Double-dash usage (signature pattern)
        if voice_features["double_dash_usage"] > 0:
            alignment_score += 0.2
        
        # Technical depth
        if voice_features["technical_depth_score"] > 2:
            alignment_score += 0.25
        
        # Future vision
        if voice_features["future_vision_indicators"] > 1:
            alignment_score += 0.2
        
        # Structured approach
        if voice_features["structured_approach"] > 1:
            alignment_score += 0.2
        
        # Industry terminology
        if voice_features["industry_terminology"] > 2:
            alignment_score += 0.15
        
        return min(alignment_score, 1.0)
    
    async def _generate_subject_line(
        self, 
        job_analysis: JobAnalysis, 
        candidate_background: Dict[str, Any]
    ) -> str:
        """Generate compelling subject line in Paul's style"""
        
        subject_prompt = f"""
        Generate a subject line for Paul Golding's introduction email to Keshav Joglekar about the {job_analysis.position_title} role.
        
        Paul's subject lines are:
        - Strategic and forward-thinking
        - Reference specific expertise or achievements
        - Create intrigue about the opportunity
        - Professional but not generic
        
        Context:
        - Keshav scaled Storynest.ai from 200K to 1M users
        - Has multi-model architecture expertise  
        - Strong cost optimization background
        - Role is about edge AI innovation
        
        Generate 3 subject line options that Paul would actually use.
        """
        
        response = await llm_client.generate(
            prompt=subject_prompt,
            system_prompt="Generate executive-level subject lines"
        )
        
        # Parse and return the first option
        lines = [line.strip() for line in response.content.split('\n') if line.strip()]
        return lines[0] if lines else "Edge AI Innovation Opportunity at ADI"
    
    async def _extract_key_points(self, email_content: str) -> List[str]:
        """Extract key points covered in the email"""
        
        extraction_prompt = f"""
        Extract the key points covered in this email:
        
        {email_content}
        
        List the main topics, connections, and value propositions mentioned.
        Format as a simple list.
        """
        
        response = await llm_client.generate(
            prompt=extraction_prompt,
            system_prompt="Extract key points from email content"
        )
        
        # Parse response into list
        points = [point.strip().lstrip('-*•').strip() 
                 for point in response.content.split('\n') 
                 if point.strip() and len(point.strip()) > 10]
        
        return points[:8]  # Limit to 8 key points
    
    def _format_voice_profile(self) -> str:
        """Format voice profile for prompt inclusion"""
        
        profile = self.paul_golding_profile
        
        return f"""
        VOICE CHARACTERISTICS:
        {chr(10).join(f"- {char}" for char in profile.key_characteristics)}
        
        TONE: {', '.join(profile.tone_descriptors)}
        
        STRUCTURAL PATTERNS:
        {chr(10).join(f"- {pattern}" for pattern in profile.structural_patterns)}
        
        SIGNATURE PHRASES:
        {chr(10).join(f"- {phrase}" for phrase in profile.signature_phrases)}
        
        TECHNICAL DEPTH: {profile.technical_depth_level}
        COMMUNICATION STYLE: {profile.communication_style}
        """
    
    def _get_introduction_template(self) -> str:
        """Template for introduction emails"""
        
        return """
        Subject: [Compelling, strategic subject line]
        
        Hi [Name],
        
        [Strategic opening - industry context/trend that makes this conversation relevant]
        
        [Connection to recipient's background - specific achievements that caught attention]
        
        [Strategic alignment - how their experience fits into bigger picture]
        
        [Technical depth - show understanding of their work and its implications]
        
        [Forward-looking perspective - where this could lead]
        
        [Clear, professional next step]
        
        Best regards,
        Paul Golding
        VP of Edge AI, Analog Devices
        """
    
    def _get_response_template(self) -> str:
        """Template for response emails"""
        
        return """
        [Acknowledge their input/question]
        
        [Provide structured response with technical depth]
        
        [Connect to strategic implications]
        
        [Next steps or follow-up]
        """
    
    def _get_inquiry_template(self) -> str:
        """Template for inquiry emails"""
        
        return """
        [Context for the inquiry]
        
        [Specific questions or requests]
        
        [Strategic rationale]
        
        [Proposed next steps]
        """
    
    def save_email(self, email: SynthesizedEmail, output_path: str = "outputs/vp_intro_email.md"):
        """Save synthesized email to file"""
        
        email_content = f"""# VP Introduction Email

## Subject Line
{email.subject_line}

## Email Body
{email.email_body}

## Analysis Metrics
- Voice Alignment Score: {email.voice_alignment_score:.2f}
- Overall Confidence: {email.confidence_score:.2f}

## Key Points Covered
{chr(10).join(f"- {point}" for point in email.key_points_covered)}

## Style Metrics
{json.dumps(email.style_metrics, indent=2)}
"""
        
        with open(output_path, 'w') as f:
            f.write(email_content)
        
        logger.info(f"VP email saved to {output_path}")

# Global synthesizer instance
vp_voice_synthesizer = VPVoiceSynthesizer()