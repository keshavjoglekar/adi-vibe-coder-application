"""
Enhanced Job Analyzer Agent - Identify what 99% of applicants will miss
"""

import json
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import asyncio
import logging

from lib.llm_client import llm_client, LLMResponse
from lib.performance_tracker import perf_tracker, track_performance
from lib.cache_manager import cache_manager

logger = logging.getLogger(__name__)

@dataclass
class WeightedRequirement:
    requirement: str
    category: str  # technical, experience, soft_skills, domain_knowledge, hidden
    importance: str  # critical, important, preferred
    weight_score: float  # 0.0 to 1.0
    evidence_needed: str
    confidence: float
    uniqueness_score: float  # How likely others are to miss this (0.0 to 1.0)
    keywords: List[str]

@dataclass
class HiddenInsight:
    insight: str
    category: str  # workflow, culture, strategic, technical, political
    why_hidden: str  # Why 99% of applicants will miss this
    importance: float  # 0.0 to 1.0
    evidence_sources: List[str]
    applicant_miss_rate: float  # 0.0 to 1.0 estimated miss rate

@dataclass
class CompetitiveAnalysis:
    total_applicants_estimated: int
    percentage_meeting_basic_reqs: float
    percentage_with_genai_experience: float
    percentage_with_exec_experience: float
    unique_differentiators: List[str]
    competitive_advantages: List[str]

@dataclass
class EnhancedJobAnalysis:
    position_title: str
    company: str
    weighted_requirements: List[WeightedRequirement]
    hidden_insights: List[HiddenInsight]
    competitive_analysis: CompetitiveAnalysis
    success_metrics: List[str]
    failure_indicators: List[str]
    technical_stack: List[str]
    cultural_signals: List[str]
    strategic_context: str
    processing_time_ms: float
    confidence_score: float
    uniqueness_analysis: Dict[str, float]

class EnhancedJobAnalyzer:
    """Enhanced job analyzer that identifies what 99% of applicants miss"""
    
    def __init__(self):
        self.hidden_insight_patterns = {
            "workflow_automation": [
                r"shadow|pair|observe|friction|touchpoint|workflow",
                r"daily|real.?time|continuous|ongoing",
                r"automate|eliminate|reduce.*\d+%"
            ],
            "executive_dynamics": [
                r"VP|executive|C.?level|senior leadership",
                r"strategic|vision|roadmap|priorities",
                r"decision.?making|influence|stakeholder"
            ],
            "cultural_uniqueness": [
                r"halo.*effect|evangeliz|broadcast|amplif",
                r"media|public|conference|demo",
                r"founding.*engineer|pioneer|first"
            ],
            "technical_sophistication": [
                r"digital.?twin|personal.?style|indistinguishable",
                r"fine.?tun|orchestrat|multi.?agent",
                r"BLEU|Turing|confusion.*rate"
            ],
            "business_context": [
                r"\$\d+.*billion|\d+,?\d+.*people|global|revenue",
                r"intelligent.*edge|semiconductor|analog",
                r"climate.*change|digital.*healthcare"
            ]
        }
    
    @track_performance("EnhancedJobAnalyzer")
    async def analyze_job_description(self, job_description: str) -> EnhancedJobAnalysis:
        """Comprehensive analysis identifying hidden requirements and insights"""
        
        start_time = time.time()
        logger.info("Starting enhanced job description analysis...")
        
        # Check cache first
        cached_result = cache_manager.get_analysis_result(
            job_description, "enhanced_job_analysis"
        )
        if cached_result:
            logger.info("Using cached job analysis result")
            return cached_result
        
        # Parallel analysis for speed
        analysis_tasks = [
            self._extract_weighted_requirements(job_description),
            self._identify_hidden_insights(job_description),
            self._analyze_competitive_landscape(job_description),
            self._extract_strategic_context(job_description)
        ]
        
        requirements, hidden_insights, competitive_analysis, strategic_context = await asyncio.gather(*analysis_tasks)
        
        # Generate additional analysis
        success_metrics = await self._extract_success_metrics(job_description)
        failure_indicators = await self._identify_failure_indicators(job_description)
        technical_stack = self._extract_technical_stack(job_description)
        cultural_signals = self._extract_cultural_signals(job_description)
        
        # Calculate uniqueness analysis
        uniqueness_analysis = self._calculate_uniqueness_scores(requirements, hidden_insights)
        
        processing_time = (time.time() - start_time) * 1000
        
        analysis = EnhancedJobAnalysis(
            position_title=self._extract_position_title(job_description),
            company=self._extract_company_name(job_description),
            weighted_requirements=requirements,
            hidden_insights=hidden_insights,
            competitive_analysis=competitive_analysis,
            success_metrics=success_metrics,
            failure_indicators=failure_indicators,
            technical_stack=technical_stack,
            cultural_signals=cultural_signals,
            strategic_context=strategic_context,
            processing_time_ms=processing_time,
            confidence_score=0.92,
            uniqueness_analysis=uniqueness_analysis
        )
        
        # Cache the result
        cache_manager.cache_analysis_result(
            job_description, "enhanced_job_analysis", analysis, cost=0.05
        )
        
        logger.info(f"Enhanced job analysis completed in {processing_time:.1f}ms")
        return analysis
    
    async def _extract_weighted_requirements(self, job_description: str) -> List[WeightedRequirement]:
        """Extract requirements with importance weights and uniqueness scores"""
        
        prompt = f"""
        Analyze this job description and extract ALL requirements with weighted importance scores.
        Focus on identifying requirements that 99% of applicants will overlook or underestimate.
        
        JOB DESCRIPTION:
        {job_description}
        
        For each requirement, provide:
        1. The exact requirement text
        2. Category: technical, experience, soft_skills, domain_knowledge, hidden
        3. Importance: critical, important, preferred  
        4. Weight score: 0.0-1.0 based on impact on success
        5. Evidence needed to prove competency
        6. Confidence in extraction: 0.0-1.0
        7. Uniqueness score: 0.0-1.0 (how likely others are to miss this)
        8. Keywords that signal this requirement
        
        SPECIAL FOCUS: Identify requirements hidden between the lines:
        - Workflow automation sophistication
        - Executive-level business acumen  
        - Real-time problem recognition
        - Digital twin development expertise
        - AI evangelism capabilities
        - Enterprise security consciousness
        
        Return as a JSON array of requirement objects.
        """
        
        response = await llm_client.generate(
            prompt=prompt,
            system_prompt="You are an expert job analysis specialist. Extract requirements with precision and identify what others miss."
        )
        
        # Parse requirements with error handling
        try:
            requirements_data = json.loads(response.content)
            requirements = []
            
            for req_data in requirements_data:
                requirement = WeightedRequirement(
                    requirement=req_data.get("requirement", ""),
                    category=req_data.get("category", "unknown"),
                    importance=req_data.get("importance", "important"),
                    weight_score=float(req_data.get("weight_score", 0.5)),
                    evidence_needed=req_data.get("evidence_needed", ""),
                    confidence=float(req_data.get("confidence", 0.8)),
                    uniqueness_score=float(req_data.get("uniqueness_score", 0.5)),
                    keywords=req_data.get("keywords", [])
                )
                requirements.append(requirement)
            
            return requirements
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse requirements JSON: {e}")
            return self._fallback_requirement_extraction(job_description)
    
    async def _identify_hidden_insights(self, job_description: str) -> List[HiddenInsight]:
        """Identify insights that 99% of applicants will miss"""
        
        prompt = f"""
        Analyze this job description to identify HIDDEN insights that 99% of applicants will miss.
        Focus on reading between the lines to understand the real challenges and opportunities.
        
        JOB DESCRIPTION:
        {job_description}
        
        Identify hidden insights in these categories:
        1. WORKFLOW INSIGHTS - How the VP actually works, pain points, friction areas
        2. CULTURAL INSIGHTS - Unspoken cultural expectations and values  
        3. STRATEGIC INSIGHTS - Business context and strategic priorities not explicitly stated
        4. TECHNICAL INSIGHTS - Advanced technical challenges hidden in simple descriptions
        5. POLITICAL INSIGHTS - Organizational dynamics and stakeholder relationships
        
        For each insight, explain:
        - The hidden insight itself
        - Why 99% of applicants will miss this
        - How important this insight is (0.0-1.0)
        - What evidence in the text supports this
        - Estimated miss rate among applicants (0.0-1.0)
        
        Return as JSON array of insight objects.
        """
        
        response = await llm_client.generate(
            prompt=prompt,
            system_prompt="You are an expert at reading between the lines in job descriptions. Identify what others miss."
        )
        
        try:
            insights_data = json.loads(response.content)
            insights = []
            
            for insight_data in insights_data:
                insight = HiddenInsight(
                    insight=insight_data.get("insight", ""),
                    category=insight_data.get("category", "unknown"),
                    why_hidden=insight_data.get("why_hidden", ""),
                    importance=float(insight_data.get("importance", 0.7)),
                    evidence_sources=insight_data.get("evidence_sources", []),
                    applicant_miss_rate=float(insight_data.get("applicant_miss_rate", 0.9))
                )
                insights.append(insight)
            
            return insights
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse insights JSON: {e}")
            return self._fallback_insight_extraction(job_description)
    
    async def _analyze_competitive_landscape(self, job_description: str) -> CompetitiveAnalysis:
        """Analyze competitive landscape and differentiation opportunities"""
        
        prompt = f"""
        Analyze the competitive landscape for this position. Estimate how many applicants will apply
        and what percentage will meet various requirements.
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide analysis of:
        1. Estimated total applicants for this type of role
        2. Percentage meeting basic technical requirements  
        3. Percentage with real GenAI product experience
        4. Percentage with executive collaboration experience
        5. Unique differentiators that would stand out
        6. Competitive advantages that matter most
        
        Consider this is a VP-level shadow role at a major semiconductor company.
        Return analysis as JSON object.
        """
        
        response = await llm_client.generate(
            prompt=prompt,
            system_prompt="You are an expert in tech hiring and competitive analysis."
        )
        
        try:
            analysis_data = json.loads(response.content)
            
            return CompetitiveAnalysis(
                total_applicants_estimated=analysis_data.get("total_applicants_estimated", 500),
                percentage_meeting_basic_reqs=float(analysis_data.get("percentage_meeting_basic_reqs", 0.3)),
                percentage_with_genai_experience=float(analysis_data.get("percentage_with_genai_experience", 0.15)),
                percentage_with_exec_experience=float(analysis_data.get("percentage_with_exec_experience", 0.05)),
                unique_differentiators=analysis_data.get("unique_differentiators", []),
                competitive_advantages=analysis_data.get("competitive_advantages", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse competitive analysis: {e}")
            return CompetitiveAnalysis(
                total_applicants_estimated=500,
                percentage_meeting_basic_reqs=0.3,
                percentage_with_genai_experience=0.15,
                percentage_with_exec_experience=0.05,
                unique_differentiators=["GenAI product shipping experience", "Executive collaboration"],
                competitive_advantages=["Scale experience", "Cost optimization", "Multi-model architecture"]
            )
    
    async def _extract_strategic_context(self, job_description: str) -> str:
        """Extract strategic business context and implications"""
        
        prompt = f"""
        Extract the strategic business context from this job description.
        What is the bigger picture this role serves? What are the business implications?
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide a concise strategic context analysis covering:
        - Business drivers for this role
        - Strategic importance to the company
        - Market context and competitive implications  
        - Technology trends this role addresses
        - Expected business impact
        
        Keep response to 2-3 paragraphs maximum.
        """
        
        response = await llm_client.generate(
            prompt=prompt,
            system_prompt="You are a business strategy consultant analyzing strategic roles."
        )
        
        return response.content.strip()
    
    async def _extract_success_metrics(self, job_description: str) -> List[str]:
        """Extract quantified success metrics"""
        
        # Look for explicit metrics in job description
        metric_patterns = [
            r'≥\s*\d+.*agents.*by.*day.*\d+',
            r'≥\s*\d+.*%.*reduction.*by.*day.*\d+',
            r'≥\s*\d+.*features.*by.*month.*\d+',
            r'≥\s*\d+.*%.*confusion.*rate',
            r'BLEU.*\d+\.\d+',
            r'>\s*\d+.*%.*touchpoints'
        ]
        
        metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            metrics.extend(matches)
        
        # Add inferred metrics
        if "digital twin" in job_description.lower():
            metrics.append("70%+ Turing test confusion rate")
        if "agents" in job_description.lower():
            metrics.append("5+ production agents within 30 days")
            
        return metrics[:8]  # Limit to top 8
    
    async def _identify_failure_indicators(self, job_description: str) -> List[str]:
        """Identify what would indicate failure in this role"""
        
        failure_indicators = [
            "Inability to ship agents on daily basis",
            "VP productivity not measurably improved by day 90",
            "Digital twin fails Turing evaluation (<70% confusion)",
            "No external media coverage by month 6",
            "Agents don't integrate with enterprise systems",
            "Cost per automation exceeds VP time value",
            "Team adoption below 25% by day 60",
            "Technical debt accumulation without measurement"
        ]
        
        return failure_indicators
    
    def _extract_technical_stack(self, job_description: str) -> List[str]:
        """Extract technical stack with enhanced pattern matching"""
        
        tech_patterns = {
            "AI/ML Frameworks": r'\b(?:LangChain|OpenAI|Claude|GPT|MCP|Anthropic|Hugging\s?Face)\b',
            "Languages": r'\b(?:Python|TypeScript|JavaScript|Go|Rust)\b',
            "Cloud/Deployment": r'\b(?:Vercel|AWS|Azure|GCP|Docker|Kubernetes)\b',
            "Enterprise APIs": r'\b(?:Teams|Confluence|Office|SharePoint|Slack)\b',
            "Databases": r'\b(?:PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
            "Monitoring": r'\b(?:telemetry|metrics|dashboard|monitoring)\b'
        }
        
        tech_stack = []
        for category, pattern in tech_patterns.items():
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                tech_stack.extend([f"{category}: {', '.join(set(matches))}"])
        
        return tech_stack
    
    def _extract_cultural_signals(self, job_description: str) -> List[str]:
        """Extract cultural signals with weighted importance"""
        
        cultural_patterns = {
            "Innovation Focus": [r"breakthrough|innovative|cutting.edge|next.generation"],
            "Speed Culture": [r"daily|rapid|fast|quick|agile|sprint"],
            "Metrics Driven": [r"metrics|measure|dashboard|KPI|ROI|impact"],
            "Executive Access": [r"VP|shadow|executive|C.level|leadership"],
            "Public Visibility": [r"media|conference|demo|evangeliz|broadcast"],
            "Startup Energy": [r"founding|pioneer|entrepreneur|hacker.*residence"]
        }
        
        signals = []
        for signal_type, patterns in cultural_patterns.items():
            for pattern in patterns:
                if re.search(pattern, job_description, re.IGNORECASE):
                    signals.append(signal_type)
                    break
        
        return list(set(signals))  # Remove duplicates
    
    def _calculate_uniqueness_scores(self, requirements: List[WeightedRequirement], insights: List[HiddenInsight]) -> Dict[str, float]:
        """Calculate uniqueness analysis scores"""
        
        # Average uniqueness of requirements
        req_uniqueness = sum(r.uniqueness_score for r in requirements) / len(requirements) if requirements else 0
        
        # Average insight miss rate
        insight_uniqueness = sum(i.applicant_miss_rate for i in insights) / len(insights) if insights else 0
        
        # Calculate categories
        hidden_req_count = len([r for r in requirements if r.category == "hidden"])
        critical_unique_count = len([r for r in requirements if r.importance == "critical" and r.uniqueness_score > 0.7])
        
        return {
            "overall_uniqueness": (req_uniqueness + insight_uniqueness) / 2,
            "hidden_requirements_found": hidden_req_count,
            "critical_unique_requirements": critical_unique_count,
            "competitive_advantage_score": min(req_uniqueness * 1.2, 1.0),
            "insight_depth_score": insight_uniqueness
        }
    
    def _fallback_requirement_extraction(self, job_description: str) -> List[WeightedRequirement]:
        """Fallback requirement extraction when JSON parsing fails"""
        
        # Simple pattern-based extraction
        requirements = []
        
        # Critical requirements patterns
        critical_patterns = [
            (r"track record.*GenAI", "technical", 0.95, 0.8),
            (r"shadow.*VP", "experience", 0.9, 0.95),
            (r"digital twin", "technical", 0.85, 0.9),
            (r"daily.*ship", "workflow", 0.8, 0.85)
        ]
        
        for pattern, category, weight, uniqueness in critical_patterns:
            if re.search(pattern, job_description, re.IGNORECASE):
                requirements.append(WeightedRequirement(
                    requirement=f"Pattern match: {pattern}",
                    category=category,
                    importance="critical",
                    weight_score=weight,
                    evidence_needed="Portfolio demonstration",
                    confidence=0.7,
                    uniqueness_score=uniqueness,
                    keywords=[pattern.replace(".*", "").replace("\\", "")]
                ))
        
        return requirements
    
    def _fallback_insight_extraction(self, job_description: str) -> List[HiddenInsight]:
        """Fallback insight extraction"""
        
        insights = [
            HiddenInsight(
                insight="Executive workflow automation requires deep business acumen understanding",
                category="workflow",
                why_hidden="Most applicants focus on technical skills, not business context",
                importance=0.9,
                evidence_sources=["VP shadow role", "strategic context"],
                applicant_miss_rate=0.85
            ),
            HiddenInsight(
                insight="Real-time friction detection demands pattern recognition at exec level",
                category="technical",
                why_hidden="Requires understanding of executive decision-making patterns",
                importance=0.85,
                evidence_sources=["capture friction points", "real-time automation"],
                applicant_miss_rate=0.9
            )
        ]
        
        return insights
    
    def _extract_position_title(self, job_description: str) -> str:
        """Enhanced position title extraction"""
        
        title_patterns = [
            r"(?i)^([^\n]+(?:coder|engineer|resident)[^\n]*)",
            r"(?i)(Vibe Coder[^\n]*)",
            r"(?i)^([^\n]+GenAI[^\n]*)",
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_description.strip())
            if match:
                return match.group(1).strip()
        
        return "Vibe Coder-in-Residence (GenAI Tech EA)"
    
    def _extract_company_name(self, job_description: str) -> str:
        """Enhanced company name extraction"""
        
        company_patterns = [
            r"(?i)Analog Devices",
            r"(?i)ADI",
            r"(?i)NASDAQ:\s*ADI"
        ]
        
        for pattern in company_patterns:
            if re.search(pattern, job_description):
                return "Analog Devices Inc."
        
        return "Company Not Specified"
    
    def save_analysis(self, analysis: EnhancedJobAnalysis, output_path: str = "outputs/enhanced_job_analysis.json"):
        """Save enhanced analysis with performance metrics"""
        
        analysis_dict = asdict(analysis)
        analysis_dict["generated_at"] = time.time()
        analysis_dict["cache_stats"] = cache_manager.get_cache_stats()
        
        with open(output_path, 'w') as f:
            json.dump(analysis_dict, f, indent=2, default=str)
        
        logger.info(f"Enhanced job analysis saved to {output_path}")

# Global enhanced analyzer instance
enhanced_job_analyzer = EnhancedJobAnalyzer()