"""
Job Analyzer Agent - Extracts requirements and identifies hidden needs from job descriptions
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio
import logging

from lib.llm_client import llm_client, LLMResponse, ModelProvider

logger = logging.getLogger(__name__)

@dataclass
class JobRequirement:
    category: str  # technical, experience, soft_skills, domain_knowledge
    requirement: str
    importance: str  # critical, important, preferred
    evidence_needed: str  # what would prove competency
    confidence: float

@dataclass
class JobAnalysis:
    position_title: str
    company: str
    key_requirements: List[JobRequirement]
    hidden_requirements: List[str]  # between-the-lines needs
    company_culture_signals: List[str]
    technical_stack: List[str]
    experience_level: str
    team_dynamics: str
    growth_opportunities: List[str]
    red_flags: List[str]
    alignment_score: float
    success_metrics: List[str]

class JobAnalyzer:
    """Advanced job description analysis with requirement extraction and cultural inference"""
    
    def __init__(self):
        self.analysis_prompt_template = """
        You are an expert job market analyst with deep experience in AI/ML and edge computing roles.
        Analyze this job description with forensic detail to extract both explicit and implicit requirements.
        
        JOB DESCRIPTION:
        {job_description}
        
        ANALYSIS FRAMEWORK:
        1. EXPLICIT REQUIREMENTS - What's directly stated
        2. IMPLICIT REQUIREMENTS - What's implied but not stated
        3. CULTURAL SIGNALS - What the language reveals about company culture
        4. TECHNICAL DEPTH - Required vs preferred technical skills
        5. STRATEGIC IMPORTANCE - How this role fits into larger business goals
        6. SUCCESS INDICATORS - What would make someone successful in this role
        
        OUTPUT REQUIREMENTS:
        - Categorize requirements by: technical, experience, soft_skills, domain_knowledge
        - Identify importance level: critical, important, preferred
        - Extract hidden requirements reading between the lines
        - Analyze cultural fit indicators
        - Assess role's strategic importance
        - Flag potential concerns or red flags
        
        Be comprehensive and analytical. This analysis will guide application strategy.
        """
    
    async def analyze_job_description(self, job_description: str) -> JobAnalysis:
        """Comprehensive analysis of job description"""
        
        logger.info("Starting job description analysis...")
        
        # Primary analysis
        analysis_response = await llm_client.generate(
            prompt=self.analysis_prompt_template.format(job_description=job_description),
            system_prompt="You are an expert job analyst. Provide detailed, structured analysis."
        )
        
        # Secondary analysis for hidden requirements
        hidden_req_response = await self._extract_hidden_requirements(job_description)
        
        # Cultural analysis
        culture_response = await self._analyze_company_culture(job_description)
        
        # Parse and structure the results
        structured_analysis = await self._structure_analysis(
            job_description,
            analysis_response.content,
            hidden_req_response.content,
            culture_response.content
        )
        
        logger.info(f"Job analysis completed with {len(structured_analysis.key_requirements)} requirements identified")
        
        return structured_analysis
    
    async def _extract_hidden_requirements(self, job_description: str) -> LLMResponse:
        """Extract implicit requirements and between-the-lines needs"""
        
        prompt = f"""
        Analyze this job description to identify HIDDEN requirements - things not explicitly stated but clearly expected:
        
        {job_description}
        
        Focus on:
        1. Implicit technical skills suggested by context
        2. Unstated experience requirements
        3. Cultural expectations from language choices
        4. Industry knowledge assumptions
        5. Soft skills implied by responsibilities
        6. Networking/relationship requirements
        
        Think like a hiring manager - what are you REALLY looking for but didn't explicitly state?
        """
        
        return await llm_client.generate(prompt, system_prompt="Extract implicit job requirements")
    
    async def _analyze_company_culture(self, job_description: str) -> LLMResponse:
        """Analyze cultural signals and company characteristics"""
        
        prompt = f"""
        Analyze the cultural signals in this job description:
        
        {job_description}
        
        Extract insights about:
        1. Company values (from language choices, priorities)
        2. Work environment (collaborative, autonomous, etc.)
        3. Growth stage (startup, scale-up, enterprise)
        4. Innovation culture (risk tolerance, experimentation)
        5. Communication style (formal, casual, direct)
        6. Team dynamics (hierarchical, flat, cross-functional)
        7. Decision-making process (data-driven, intuitive, consensus)
        
        What does the language tell us about working there?
        """
        
        return await llm_client.generate(prompt, system_prompt="Analyze company culture from job posting")
    
    async def _structure_analysis(
        self,
        job_description: str,
        main_analysis: str,
        hidden_requirements: str,
        culture_analysis: str
    ) -> JobAnalysis:
        """Structure the analysis into standardized format"""
        
        # Extract position and company info
        position_title = self._extract_position_title(job_description)
        company = self._extract_company_name(job_description)
        
        # Parse requirements using structured prompt
        requirements = await self._parse_requirements(main_analysis)
        
        # Extract specific analysis components
        hidden_reqs = self._extract_list_items(hidden_requirements)
        culture_signals = self._extract_list_items(culture_analysis)
        tech_stack = self._extract_technical_stack(job_description)
        
        return JobAnalysis(
            position_title=position_title,
            company=company,
            key_requirements=requirements,
            hidden_requirements=hidden_reqs[:10],  # Top 10
            company_culture_signals=culture_signals[:8],
            technical_stack=tech_stack,
            experience_level=self._determine_experience_level(job_description),
            team_dynamics=self._extract_team_dynamics(culture_analysis),
            growth_opportunities=self._extract_growth_opportunities(job_description),
            red_flags=self._identify_red_flags(job_description),
            alignment_score=0.85,  # Placeholder - would be calculated based on user profile
            success_metrics=self._extract_success_metrics(main_analysis)
        )
    
    async def _parse_requirements(self, analysis_text: str) -> List[JobRequirement]:
        """Parse requirements from analysis text into structured format"""
        
        # Use LLM to structure the requirements
        structure_prompt = f"""
        Extract and structure job requirements from this analysis:
        
        {analysis_text}
        
        For each requirement, provide:
        - category: technical/experience/soft_skills/domain_knowledge
        - requirement: specific requirement description
        - importance: critical/important/preferred
        - evidence_needed: what would prove this competency
        - confidence: 0.0-1.0 score for extraction confidence
        
        Format as JSON array of requirement objects.
        """
        
        response = await llm_client.generate(
            prompt=structure_prompt,
            system_prompt="Structure job requirements as JSON. Be precise and comprehensive."
        )
        
        # Parse JSON response
        try:
            requirements_data = json.loads(response.content)
            parsed_requirements = []
            for req in requirements_data:
                if isinstance(req, dict):
                    parsed_requirements.append(JobRequirement(**req))
                else:
                    logger.warning(f"Invalid requirement format: {req}")
            return parsed_requirements
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.warning(f"Could not parse requirements JSON ({e}), using fallback parsing")
            return self._fallback_requirement_parsing(analysis_text)
    
    def _fallback_requirement_parsing(self, text: str) -> List[JobRequirement]:
        """Fallback method to parse requirements if JSON parsing fails"""
        
        requirements = []
        
        # Simple pattern-based extraction
        patterns = {
            "technical": r"(?i)(programming|software|system|architecture|framework|technology|tool)",
            "experience": r"(?i)(years|experience|background|history|previous)",
            "soft_skills": r"(?i)(communication|leadership|teamwork|collaboration|problem.solving)",
            "domain_knowledge": r"(?i)(domain|industry|business|market|sector)"
        }
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ["require", "need", "must", "should"]):
                category = "experience"  # default
                for cat, pattern in patterns.items():
                    if re.search(pattern, sentence):
                        category = cat
                        break
                
                requirements.append(JobRequirement(
                    category=category,
                    requirement=sentence.strip(),
                    importance="important",
                    evidence_needed="Portfolio or experience demonstration",
                    confidence=0.7
                ))
        
        return requirements[:15]  # Limit to prevent overflow
    
    def _extract_position_title(self, job_description: str) -> str:
        """Extract position title from job description"""
        
        # Look for common patterns
        title_patterns = [
            r"(?i)position[:\s]+([^\n]+)",
            r"(?i)role[:\s]+([^\n]+)",
            r"(?i)job title[:\s]+([^\n]+)",
            r"(?i)we are hiring[:\s]+([^\n]+)"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_description)
            if match:
                return match.group(1).strip()
        
        # Fallback to first line if it looks like a title
        first_line = job_description.split('\n')[0].strip()
        if len(first_line) < 100 and any(word in first_line.lower() for word in ["engineer", "developer", "manager", "analyst", "specialist"]):
            return first_line
        
        return "Position Not Specified"
    
    def _extract_company_name(self, job_description: str) -> str:
        """Extract company name from job description"""
        
        company_patterns = [
            r"(?i)company[:\s]+([^\n]+)",
            r"(?i)at\s+([A-Z][a-zA-Z\s&]+)(?:\s|,|\.)",
            r"(?i)join\s+([A-Z][a-zA-Z\s&]+)(?:\s|,|\.)"
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, job_description)
            if match:
                company = match.group(1).strip()
                # Clean up common suffixes
                company = re.sub(r'\s+(Inc|LLC|Corp|Corporation|Ltd)\.?$', '', company)
                return company
        
        return "Company Not Specified"
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text"""
        
        items = []
        
        # Look for numbered lists
        numbered_items = re.findall(r'(?:^|\n)\s*\d+\.?\s*([^\n]+)', text, re.MULTILINE)
        items.extend(numbered_items)
        
        # Look for bulleted lists
        bullet_items = re.findall(r'(?:^|\n)\s*[-*•]\s*([^\n]+)', text, re.MULTILINE)
        items.extend(bullet_items)
        
        # Clean and filter
        items = [item.strip() for item in items if len(item.strip()) > 10]
        
        return items
    
    def _extract_technical_stack(self, job_description: str) -> List[str]:
        """Extract technical stack from job description"""
        
        # Common tech terms
        tech_patterns = [
            r'\b(?:Python|JavaScript|Java|C\+\+|Go|Rust|TypeScript)\b',
            r'\b(?:React|Vue|Angular|Node\.js|Django|Flask|FastAPI)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Terraform)\b',
            r'\b(?:PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
            r'\b(?:TensorFlow|PyTorch|scikit-learn|Pandas|NumPy)\b',
            r'\b(?:Git|Jenkins|CI/CD|Agile|Scrum)\b'
        ]
        
        tech_stack = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            tech_stack.extend(matches)
        
        return list(set(tech_stack))  # Remove duplicates
    
    def _determine_experience_level(self, job_description: str) -> str:
        """Determine required experience level"""
        
        if re.search(r'(?i)(\d+)\+?\s*years', job_description):
            years_match = re.search(r'(?i)(\d+)\+?\s*years', job_description)
            years = int(years_match.group(1))
            
            if years <= 2:
                return "Junior"
            elif years <= 5:
                return "Mid-level"
            elif years <= 10:
                return "Senior"
            else:
                return "Principal/Staff"
        
        # Look for level indicators
        if any(word in job_description.lower() for word in ["junior", "entry", "associate"]):
            return "Junior"
        elif any(word in job_description.lower() for word in ["senior", "lead", "principal"]):
            return "Senior+"
        
        return "Mid-level"
    
    def _extract_team_dynamics(self, culture_analysis: str) -> str:
        """Extract team dynamics from culture analysis"""
        
        if "collaborative" in culture_analysis.lower():
            return "Collaborative"
        elif "autonomous" in culture_analysis.lower():
            return "Autonomous"
        elif "hierarchical" in culture_analysis.lower():
            return "Hierarchical"
        else:
            return "Cross-functional"
    
    def _extract_growth_opportunities(self, job_description: str) -> List[str]:
        """Extract growth and development opportunities"""
        
        growth_indicators = []
        
        growth_patterns = [
            r"(?i)(career development|professional growth|learning opportunities)",
            r"(?i)(mentorship|training|certification|conference)",
            r"(?i)(promotion|advancement|leadership)",
            r"(?i)(innovative projects|cutting-edge|research)"
        ]
        
        for pattern in growth_patterns:
            if re.search(pattern, job_description):
                growth_indicators.append(re.search(pattern, job_description).group(1))
        
        return growth_indicators
    
    def _identify_red_flags(self, job_description: str) -> List[str]:
        """Identify potential red flags in job description"""
        
        red_flags = []
        
        flag_patterns = {
            "Unrealistic expectations": r"(?i)(rock star|ninja|guru|10x|unicorn)",
            "Work-life balance concerns": r"(?i)(fast-paced|high-pressure|long hours|weekends)",
            "Vague responsibilities": r"(?i)(other duties as assigned|wearing many hats)",
            "Compensation concerns": r"(?i)(competitive salary|DOE|equity only)"
        }
        
        for flag, pattern in flag_patterns.items():
            if re.search(pattern, job_description):
                red_flags.append(flag)
        
        return red_flags
    
    def _extract_success_metrics(self, analysis_text: str) -> List[str]:
        """Extract success metrics from analysis"""
        
        metric_patterns = [
            r"(?i)(success|successful|achieve|deliver|improve).*?(?=\.|,|\n)",
            r"(?i)(kpi|metric|measure|target|goal).*?(?=\.|,|\n)"
        ]
        
        metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, analysis_text)
            metrics.extend(matches[:3])  # Limit to 3 per pattern
        
        return metrics[:5]  # Total limit
    
    def save_analysis(self, analysis: JobAnalysis, output_path: str = "outputs/job_analysis.json"):
        """Save analysis to JSON file"""
        
        analysis_dict = asdict(analysis)
        
        with open(output_path, 'w') as f:
            json.dump(analysis_dict, f, indent=2)
        
        logger.info(f"Job analysis saved to {output_path}")

# Global analyzer instance
job_analyzer = JobAnalyzer()