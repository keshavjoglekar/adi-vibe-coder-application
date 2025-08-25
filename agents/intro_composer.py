"""
Intro Composer Agent - Creates personalized introductions using Keshav's background and voice
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio
import logging

from lib.llm_client import llm_client, LLMResponse
from lib.style_analyzer import style_analyzer
from agents.job_analyzer import JobAnalysis, JobRequirement

logger = logging.getLogger(__name__)

@dataclass
class IntroSection:
    section_name: str
    content: str
    key_points: List[str]
    relevance_score: float
    word_count: int

@dataclass
class PersonalizedIntro:
    opening_hook: str
    sections: List[IntroSection]
    closing_statement: str
    call_to_action: str
    total_word_count: int
    alignment_score: float
    key_achievements_highlighted: List[str]
    voice_authenticity_score: float

class IntroComposer:
    """Creates compelling personal introductions that highlight relevant experience"""
    
    def __init__(self):
        self.keshav_background = {
            "name": "Keshav Joglekar",
            "current_role": "AI Strategist & Independent GenAI Engineer",
            "key_achievement": {
                "company": "Storynest.ai",
                "role": "Founding hire",
                "metrics": {
                    "user_growth": "200K to 1M users (5x growth)",
                    "cost_optimization": "Reduced COGS by 54%, margins to 73%",
                    "conversion_rate": "79% visitor-to-signup (3x industry standard)",
                    "technical_architecture": "6 LLM frameworks, 98% uptime",
                    "product_innovation": "Interactive AI stories with character dialogue"
                }
            },
            "additional_context": {
                "gaming_achievement": "Top 50 shortlisted in coding challenge",
                "enterprise_impact": "€700K savings at ESB, 4,600 vendor ecosystem",
                "current_tools": ["N8N", "Lovable", "Cursor", "Claude Code", "Windsurf", "Emergent"],
                "leadership": "International team leadership experience",
                "unique_background": "Former scuba instructor (teaching under pressure)"
            },
            "writing_style": {
                "authenticity_markers": ["actually", "honestly"],
                "approach": "Story-driven with natural metrics integration",
                "tone": "Authentic enthusiasm with future-focused vision",
                "strengths": ["Quantified achievements", "Personal narrative", "Technical depth"]
            }
        }
        
        self.intro_templates = {
            "technical_leader": self._get_technical_leader_template(),
            "scale_expert": self._get_scale_expert_template(),
            "ai_innovator": self._get_ai_innovator_template(),
            "cost_optimizer": self._get_cost_optimizer_template()
        }
    
    async def compose_introduction(
        self, 
        job_analysis: JobAnalysis,
        target_audience: str = "technical_executive",
        max_words: int = 300
    ) -> PersonalizedIntro:
        """Compose personalized introduction based on job requirements"""
        
        logger.info(f"Composing introduction for {job_analysis.position_title} at {job_analysis.company}")
        
        # Analyze job requirements to determine best positioning
        positioning_strategy = await self._determine_positioning(job_analysis)
        
        # Select most relevant template
        template_type = self._select_template(positioning_strategy, job_analysis)
        
        # Generate introduction sections
        sections = await self._generate_sections(job_analysis, positioning_strategy, template_type)
        
        # Create opening hook and closing
        opening_hook = await self._generate_opening_hook(job_analysis, positioning_strategy)
        closing_statement = await self._generate_closing(job_analysis)
        call_to_action = await self._generate_call_to_action(job_analysis)
        
        # Calculate metrics
        total_words = sum(section.word_count for section in sections) + len(opening_hook.split()) + len(closing_statement.split())
        alignment_score = await self._calculate_alignment_score(job_analysis, sections)
        voice_score = await self._validate_voice_authenticity(sections)
        
        return PersonalizedIntro(
            opening_hook=opening_hook,
            sections=sections,
            closing_statement=closing_statement,
            call_to_action=call_to_action,
            total_word_count=total_words,
            alignment_score=alignment_score,
            key_achievements_highlighted=self._extract_highlighted_achievements(sections),
            voice_authenticity_score=voice_score
        )
    
    async def _determine_positioning(self, job_analysis: JobAnalysis) -> Dict[str, Any]:
        """Determine optimal positioning strategy based on job requirements"""
        
        # Analyze job requirements to find best positioning angles
        positioning_prompt = f"""
        Analyze these job requirements to determine how Keshav Joglekar should position himself:
        
        JOB REQUIREMENTS:
        {chr(10).join(f"- {req.requirement}" for req in job_analysis.key_requirements[:10])}
        
        HIDDEN REQUIREMENTS:
        {chr(10).join(f"- {req}" for req in job_analysis.hidden_requirements[:5])}
        
        KESHAV'S BACKGROUND:
        - Scaling experience: 200K → 1M users (5x growth)
        - Cost optimization: 54% COGS reduction, 73% margins
        - Technical depth: 6 LLM frameworks, 98% uptime
        - Conversion expertise: 79% rate (3x industry standard)
        - Enterprise impact: €700K savings, 4,600 vendor ecosystem
        
        POSITIONING ANALYSIS:
        1. Which of Keshav's achievements most directly address the job requirements?
        2. What positioning themes would resonate (scale expert, cost optimizer, technical leader, AI innovator)?
        3. Which specific metrics should be emphasized?
        4. What narrative would be most compelling for this role?
        5. How should technical depth be balanced with business impact?
        
        Provide strategic positioning recommendations.
        """
        
        response = await llm_client.generate(
            prompt=positioning_prompt,
            system_prompt="Analyze positioning strategy for job applications"
        )
        
        return {
            "primary_angle": "Scale and optimization expert",
            "key_metrics": ["5x user growth", "54% cost reduction", "79% conversion rate"],
            "narrative_focus": "Technical leader who drives measurable business impact",
            "differentiation": "Multi-model architecture expertise with proven scale",
            "strategic_insight": response.content[:200]
        }
    
    def _select_template(self, positioning_strategy: Dict[str, Any], job_analysis: JobAnalysis) -> str:
        """Select most appropriate introduction template"""
        
        # Analyze job requirements to choose template
        tech_requirements = [req for req in job_analysis.key_requirements if req.category == "technical"]
        experience_requirements = [req for req in job_analysis.key_requirements if req.category == "experience"]
        
        # Decision logic based on job analysis
        if len(tech_requirements) > 3 and "architect" in job_analysis.position_title.lower():
            return "technical_leader"
        elif any("scale" in req.requirement.lower() for req in job_analysis.key_requirements):
            return "scale_expert"
        elif any("ai" in req.requirement.lower() or "ml" in req.requirement.lower() for req in job_analysis.key_requirements):
            return "ai_innovator"
        elif any("cost" in req.requirement.lower() or "efficiency" in req.requirement.lower() for req in job_analysis.key_requirements):
            return "cost_optimizer"
        else:
            return "technical_leader"  # Default
    
    async def _generate_sections(
        self, 
        job_analysis: JobAnalysis,
        positioning_strategy: Dict[str, Any],
        template_type: str
    ) -> List[IntroSection]:
        """Generate introduction sections based on template and positioning"""
        
        sections = []
        
        # Section 1: Current Role & Expertise
        current_role_section = await self._generate_current_role_section(job_analysis, positioning_strategy)
        sections.append(current_role_section)
        
        # Section 2: Key Achievement (Storynest)
        achievement_section = await self._generate_achievement_section(job_analysis, positioning_strategy)
        sections.append(achievement_section)
        
        # Section 3: Technical Depth (if relevant)
        if template_type in ["technical_leader", "ai_innovator"]:
            technical_section = await self._generate_technical_section(job_analysis)
            sections.append(technical_section)
        
        # Section 4: Unique Value Proposition
        unique_value_section = await self._generate_unique_value_section(job_analysis, positioning_strategy)
        sections.append(unique_value_section)
        
        return sections
    
    async def _generate_current_role_section(
        self, 
        job_analysis: JobAnalysis, 
        positioning_strategy: Dict[str, Any]
    ) -> IntroSection:
        """Generate current role and expertise section"""
        
        section_prompt = f"""
        Write Keshav's current role section for introduction to {job_analysis.company} {job_analysis.position_title}:
        
        POSITIONING: {positioning_strategy['narrative_focus']}
        
        CURRENT ROLE: AI Strategist & Independent GenAI Engineer
        TOOLS: N8N, Lovable, Cursor, Claude Code, Windsurf, Emergent
        
        Write in Keshav's authentic voice:
        - Use "actually" or "honestly" naturally
        - Show genuine enthusiasm for AI innovation
        - Connect current work to their needs
        - Keep it conversational but professional
        - 40-50 words max
        
        Focus on how current work aligns with their edge AI initiatives.
        """
        
        response = await llm_client.generate(
            prompt=section_prompt,
            system_prompt=style_analyzer.generate_style_prompt("keshav", f"introduction for {job_analysis.position_title}")
        )
        
        return IntroSection(
            section_name="Current Role & Expertise",
            content=response.content.strip(),
            key_points=["AI Strategy", "GenAI Engineering", "Modern AI Tools"],
            relevance_score=0.85,
            word_count=len(response.content.split())
        )
    
    async def _generate_achievement_section(
        self, 
        job_analysis: JobAnalysis, 
        positioning_strategy: Dict[str, Any]
    ) -> IntroSection:
        """Generate key achievement section highlighting Storynest impact"""
        
        # Determine which metrics to emphasize based on job requirements
        relevant_metrics = self._select_relevant_metrics(job_analysis, positioning_strategy)
        
        achievement_prompt = f"""
        Write Keshav's Storynest achievement section for {job_analysis.company}:
        
        CONTEXT: Founding hire at Storynest.ai
        RELEVANT METRICS: {relevant_metrics}
        POSITIONING: {positioning_strategy['primary_angle']}
        
        FULL STORYNEST METRICS:
        - User Growth: 200K → 1M users (5x growth)
        - Cost Optimization: Reduced COGS by 54%, margins to 73%
        - Conversion: 79% visitor-to-signup (3x industry standard)  
        - Technical: 6 LLM frameworks, 98% uptime
        - Product: Interactive AI stories with character dialogue
        
        Write in Keshav's voice:
        - Lead with the most relevant metric
        - Show story-driven narrative
        - Include specific numbers naturally
        - Connect to what they need
        - 60-80 words
        
        Make it feel authentic, not like a resume bullet point.
        """
        
        response = await llm_client.generate(
            prompt=achievement_prompt,
            system_prompt=style_analyzer.generate_style_prompt("keshav", "storytelling with metrics")
        )
        
        return IntroSection(
            section_name="Key Achievement",
            content=response.content.strip(),
            key_points=relevant_metrics,
            relevance_score=0.92,
            word_count=len(response.content.split())
        )
    
    async def _generate_technical_section(self, job_analysis: JobAnalysis) -> IntroSection:
        """Generate technical depth section if relevant to role"""
        
        technical_prompt = f"""
        Write Keshav's technical depth section for {job_analysis.position_title}:
        
        TECHNICAL BACKGROUND:
        - Multi-model LLM architecture (6 frameworks)
        - 98% system uptime at scale
        - Enterprise integration (4,600 vendor ecosystem)
        - Modern AI tools expertise
        - International team leadership
        
        JOB TECH REQUIREMENTS: {job_analysis.technical_stack}
        
        Write in Keshav's authentic style:
        - Show depth without overwhelming
        - Connect to their technical needs
        - Mention relevant technologies
        - Include system reliability focus
        - 40-60 words
        """
        
        response = await llm_client.generate(
            prompt=technical_prompt,
            system_prompt=style_analyzer.generate_style_prompt("keshav", "technical expertise explanation")
        )
        
        return IntroSection(
            section_name="Technical Depth",
            content=response.content.strip(),
            key_points=["Multi-model Architecture", "System Reliability", "Enterprise Scale"],
            relevance_score=0.78,
            word_count=len(response.content.split())
        )
    
    async def _generate_unique_value_section(
        self, 
        job_analysis: JobAnalysis, 
        positioning_strategy: Dict[str, Any]
    ) -> IntroSection:
        """Generate unique value proposition section"""
        
        unique_value_prompt = f"""
        Write Keshav's unique value section for {job_analysis.company} {job_analysis.position_title}:
        
        UNIQUE ELEMENTS:
        - Former scuba instructor (teaching under pressure)
        - Top 50 in gaming coding challenge  
        - €700K enterprise savings impact
        - International team leadership
        - Current with cutting-edge AI tools
        
        COMPANY NEEDS: Focus on edge AI innovation and scale
        
        Write in Keshav's voice:
        - Highlight what makes him different
        - Connect unique background to role value
        - Show learning agility and pressure handling
        - Future-focused perspective
        - 50-70 words
        
        Make the unique background relevant to their needs.
        """
        
        response = await llm_client.generate(
            prompt=unique_value_prompt,
            system_prompt=style_analyzer.generate_style_prompt("keshav", "unique value proposition")
        )
        
        return IntroSection(
            section_name="Unique Value",
            content=response.content.strip(),
            key_points=["Pressure Performance", "Learning Agility", "Enterprise Impact"],
            relevance_score=0.74,
            word_count=len(response.content.split())
        )
    
    def _select_relevant_metrics(self, job_analysis: JobAnalysis, positioning_strategy: Dict[str, Any]) -> List[str]:
        """Select most relevant metrics based on job requirements"""
        
        all_metrics = {
            "5x user growth": ["scale", "growth", "user"],
            "54% cost reduction": ["cost", "efficiency", "optimization", "margin"],
            "79% conversion rate": ["conversion", "performance", "user experience"],
            "98% uptime": ["reliability", "technical", "system", "infrastructure"],
            "6 LLM frameworks": ["ai", "ml", "technical", "architecture"],
            "€700K savings": ["enterprise", "business impact", "cost"]
        }
        
        relevant_metrics = []
        
        for metric, keywords in all_metrics.items():
            # Check if any keywords appear in job requirements
            job_text = " ".join([req.requirement.lower() for req in job_analysis.key_requirements])
            if any(keyword in job_text for keyword in keywords):
                relevant_metrics.append(metric)
        
        # Ensure we have at least 2-3 relevant metrics
        if len(relevant_metrics) < 2:
            relevant_metrics.extend(["5x user growth", "54% cost reduction"])
        
        return relevant_metrics[:3]
    
    async def _generate_opening_hook(
        self, 
        job_analysis: JobAnalysis, 
        positioning_strategy: Dict[str, Any]
    ) -> str:
        """Generate compelling opening hook"""
        
        hook_prompt = f"""
        Write an opening hook for Keshav's introduction to {job_analysis.company}:
        
        POSITION: {job_analysis.position_title}
        POSITIONING: {positioning_strategy['primary_angle']}
        
        Requirements:
        - Start with authentic enthusiasm  
        - Reference the specific role/company
        - Set up the value story
        - Use Keshav's natural voice
        - 15-25 words max
        
        Examples of Keshav's style:
        "I'm honestly excited about..."
        "Actually, I've been following..."
        "The opportunity at [company] really resonates..."
        
        Make it feel genuine, not generic.
        """
        
        response = await llm_client.generate(
            prompt=hook_prompt,
            system_prompt=style_analyzer.generate_style_prompt("keshav", "opening hook for introduction")
        )
        
        return response.content.strip()
    
    async def _generate_closing(self, job_analysis: JobAnalysis) -> str:
        """Generate closing statement"""
        
        closing_prompt = f"""
        Write a closing statement for Keshav's introduction to {job_analysis.company}:
        
        ROLE: {job_analysis.position_title}
        
        Requirements:
        - Forward-looking perspective
        - Connect to their mission/impact
        - Show genuine interest
        - Keshav's authentic voice
        - 20-30 words
        
        Focus on the future potential and shared vision.
        """
        
        response = await llm_client.generate(
            prompt=closing_prompt,
            system_prompt=style_analyzer.generate_style_prompt("keshav", "closing statement")
        )
        
        return response.content.strip()
    
    async def _generate_call_to_action(self, job_analysis: JobAnalysis) -> str:
        """Generate appropriate call to action"""
        
        cta_options = [
            "I'd love to discuss how this experience could contribute to ADI's edge AI initiatives.",
            "I'm excited to explore how we could accelerate edge AI innovation together.",
            "I'd welcome the opportunity to discuss the technical and strategic challenges ahead.",
            "Looking forward to connecting about the future of edge AI at ADI."
        ]
        
        # Select based on job analysis (simple selection for now)
        if "technical" in job_analysis.position_title.lower():
            return cta_options[2]
        elif "strategy" in job_analysis.position_title.lower():
            return cta_options[1]
        else:
            return cta_options[0]
    
    async def _calculate_alignment_score(self, job_analysis: JobAnalysis, sections: List[IntroSection]) -> float:
        """Calculate how well introduction aligns with job requirements"""
        
        # Simple scoring based on relevance scores and requirement coverage
        avg_relevance = sum(section.relevance_score for section in sections) / len(sections)
        
        # Bonus for covering critical requirements
        critical_reqs = [req for req in job_analysis.key_requirements if req.importance == "critical"]
        coverage_bonus = len(critical_reqs) * 0.05 if critical_reqs else 0
        
        return min(avg_relevance + coverage_bonus, 1.0)
    
    async def _validate_voice_authenticity(self, sections: List[IntroSection]) -> float:
        """Validate authenticity of Keshav's voice in introduction"""
        
        full_content = " ".join(section.content for section in sections)
        voice_features = style_analyzer.extract_keshav_voice_features(full_content)
        
        return voice_features.get("authenticity_score", 75) / 100.0
    
    def _extract_highlighted_achievements(self, sections: List[IntroSection]) -> List[str]:
        """Extract key achievements highlighted in introduction"""
        
        achievements = []
        for section in sections:
            achievements.extend(section.key_points)
        
        return list(set(achievements))  # Remove duplicates
    
    def _get_technical_leader_template(self) -> str:
        return "Opening + Current Role + Achievement (technical focus) + Technical Depth + Unique Value + Closing"
    
    def _get_scale_expert_template(self) -> str:
        return "Opening + Current Role + Achievement (scale focus) + Enterprise Experience + Unique Value + Closing"
    
    def _get_ai_innovator_template(self) -> str:
        return "Opening + Current Role + Achievement (AI focus) + Technical Innovation + Future Vision + Closing"
    
    def _get_cost_optimizer_template(self) -> str:
        return "Opening + Current Role + Achievement (optimization focus) + Business Impact + Unique Value + Closing"
    
    def save_introduction(self, intro: PersonalizedIntro, output_path: str = "outputs/personal_intro.md"):
        """Save personalized introduction to file"""
        
        intro_content = f"""# Personal Introduction

## Opening Hook
{intro.opening_hook}

## Introduction Sections

{chr(10).join(f"### {section.section_name}{chr(10)}{section.content}{chr(10)}" for section in intro.sections)}

## Closing Statement
{intro.closing_statement}

## Call to Action
{intro.call_to_action}

## Metrics
- Total Word Count: {intro.total_word_count}
- Alignment Score: {intro.alignment_score:.2f}
- Voice Authenticity: {intro.voice_authenticity_score:.2f}

## Key Achievements Highlighted
{chr(10).join(f"- {achievement}" for achievement in intro.key_achievements_highlighted)}
"""
        
        with open(output_path, 'w') as f:
            f.write(intro_content)
        
        logger.info(f"Personal introduction saved to {output_path}")

# Global composer instance
intro_composer = IntroComposer()