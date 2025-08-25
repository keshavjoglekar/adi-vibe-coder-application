#!/usr/bin/env python3
"""
Main Orchestrator - Coordinates all agents for end-to-end AI application workflow

This script demonstrates the sophisticated AI agent system built for the 
Analog Devices Vibe Coder-in-Residence application.

Usage:
    python run_application.py [--job-description FILE] [--publish] [--verbose]
    
Example:
    python run_application.py --job-description job_desc.txt --publish --verbose
"""

import os
import sys
import argparse
import asyncio
import logging
import time
from typing import Dict, Any
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.job_analyzer import job_analyzer, JobAnalysis
from agents.vp_voice_synthesizer import vp_voice_synthesizer, SynthesizedEmail  
from agents.intro_composer import intro_composer, PersonalizedIntro
from agents.github_publisher import github_publisher_agent, PublishReport
from agents.meta_agent import meta_agent, SystemAnalysis
from lib.llm_client import llm_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIApplicationOrchestrator:
    """Main orchestrator for the AI agent application system"""
    
    def __init__(self):
        self.start_time = None
        self.execution_metrics = {}
        
        # Keshav's background data
        self.candidate_background = {
            "name": "Keshav Joglekar",
            "current_role": "AI Strategist & Independent GenAI Engineer",
            "key_achievement": "Storynest.ai founding hire - 200K to 1M users (5x growth)",
            "technical_strengths": [
                "Multi-model LLM architecture (6 frameworks)",
                "Cost optimization (54% COGS reduction)", 
                "Scale experience (98% uptime at 1M users)",
                "Conversion optimization (79% rate, 3x industry standard)"
            ],
            "enterprise_impact": "€700K savings at ESB, 4,600 vendor ecosystem management",
            "unique_background": "Former scuba instructor, top 50 coding challenge",
            "current_tools": ["N8N", "Lovable", "Cursor", "Claude Code", "Windsurf", "Emergent"],
            "leadership_experience": "International team leadership",
            "achievements": {
                "user_growth": "200K → 1M users (5x)",
                "cost_optimization": "54% COGS reduction, 73% margins",
                "conversion_rate": "79% visitor-to-signup (3x industry)",
                "technical_reliability": "98% uptime with 6 LLM frameworks",
                "product_innovation": "Interactive AI stories with character dialogue"
            }
        }
    
    async def run_complete_workflow(
        self, 
        job_description: str, 
        publish_to_github: bool = False,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Execute the complete AI agent workflow"""
        
        logger.info("🚀 Starting AI Agent System for ADI Application")
        logger.info("=" * 60)
        
        self.start_time = time.time()
        results = {}
        
        try:
            # Phase 1: Job Analysis
            logger.info("📋 Phase 1: Analyzing Job Description...")
            job_analysis = await self._execute_job_analysis(job_description)
            results["job_analysis"] = job_analysis
            
            if verbose:
                self._print_job_analysis_summary(job_analysis)
            
            # Phase 2: VP Voice Synthesis
            logger.info("🎯 Phase 2: Generating VP Introduction Email...")
            vp_email = await self._execute_vp_voice_synthesis(job_analysis)
            results["vp_email"] = vp_email
            
            if verbose:
                self._print_vp_email_summary(vp_email)
            
            # Phase 3: Personal Introduction
            logger.info("✍️  Phase 3: Composing Personal Introduction...")
            personal_intro = await self._execute_intro_composition(job_analysis)
            results["personal_intro"] = personal_intro
            
            if verbose:
                self._print_intro_summary(personal_intro)
            
            # Phase 4: Meta Analysis
            logger.info("🔍 Phase 4: Analyzing System Performance...")
            system_analysis = await self._execute_meta_analysis(job_analysis, vp_email, personal_intro)
            results["system_analysis"] = system_analysis
            
            if verbose:
                self._print_system_analysis_summary(system_analysis)
            
            # Phase 5: GitHub Publishing (optional)
            if publish_to_github:
                logger.info("📤 Phase 5: Publishing to GitHub...")
                publish_report = await self._execute_github_publishing(job_analysis, vp_email, personal_intro)
                results["publish_report"] = publish_report
                
                if verbose:
                    self._print_publish_summary(publish_report)
            
            # Generate final metrics
            self._calculate_final_metrics(results)
            
            # Print success summary
            self._print_success_summary(results, verbose)
            
            logger.info("✅ AI Agent System completed successfully!")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ System execution failed: {e}")
            raise
    
    async def _execute_job_analysis(self, job_description: str) -> JobAnalysis:
        """Execute job analysis phase"""
        
        phase_start = time.time()
        
        # Analyze the job description
        analysis = await job_analyzer.analyze_job_description(job_description)
        
        # Save results
        job_analyzer.save_analysis(analysis)
        
        phase_time = time.time() - phase_start
        self.execution_metrics["job_analysis_time"] = phase_time
        
        logger.info(f"   ✓ Job analysis completed in {phase_time:.1f}s")
        logger.info(f"   ✓ Identified {len(analysis.key_requirements)} requirements")
        logger.info(f"   ✓ Discovered {len(analysis.hidden_requirements)} hidden requirements")
        
        return analysis
    
    async def _execute_vp_voice_synthesis(self, job_analysis: JobAnalysis) -> SynthesizedEmail:
        """Execute VP voice synthesis phase"""
        
        phase_start = time.time()
        
        # Generate VP-style email
        email = await vp_voice_synthesizer.generate_intro_email(
            job_analysis=job_analysis,
            candidate_background=self.candidate_background,
            context="application"
        )
        
        # Save results
        vp_voice_synthesizer.save_email(email)
        
        phase_time = time.time() - phase_start
        self.execution_metrics["vp_synthesis_time"] = phase_time
        
        logger.info(f"   ✓ VP email synthesis completed in {phase_time:.1f}s")
        logger.info(f"   ✓ Voice alignment score: {email.voice_alignment_score:.1%}")
        logger.info(f"   ✓ Covered {len(email.key_points_covered)} key points")
        
        return email
    
    async def _execute_intro_composition(self, job_analysis: JobAnalysis) -> PersonalizedIntro:
        """Execute personal introduction composition phase"""
        
        phase_start = time.time()
        
        # Compose personal introduction
        intro = await intro_composer.compose_introduction(
            job_analysis=job_analysis,
            target_audience="technical_executive", 
            max_words=300
        )
        
        # Save results
        intro_composer.save_introduction(intro)
        
        phase_time = time.time() - phase_start
        self.execution_metrics["intro_composition_time"] = phase_time
        
        logger.info(f"   ✓ Introduction composition completed in {phase_time:.1f}s")
        logger.info(f"   ✓ Job alignment score: {intro.alignment_score:.1%}")
        logger.info(f"   ✓ Voice authenticity: {intro.voice_authenticity_score:.1%}")
        
        return intro
    
    async def _execute_meta_analysis(
        self, 
        job_analysis: JobAnalysis, 
        vp_email: SynthesizedEmail, 
        personal_intro: PersonalizedIntro
    ) -> SystemAnalysis:
        """Execute meta analysis phase"""
        
        phase_start = time.time()
        
        # Analyze system performance
        analysis = await meta_agent.analyze_system_performance(job_analysis, vp_email, personal_intro)
        
        # Generate transparency report
        meta_agent.generate_transparency_report(analysis)
        meta_agent.save_analysis(analysis)
        
        phase_time = time.time() - phase_start
        self.execution_metrics["meta_analysis_time"] = phase_time
        
        logger.info(f"   ✓ Meta analysis completed in {phase_time:.1f}s")
        logger.info(f"   ✓ Overall confidence: {analysis.overall_confidence:.1%}")
        logger.info(f"   ✓ {len(analysis.success_indicators)} success indicators identified")
        
        return analysis
    
    async def _execute_github_publishing(
        self, 
        job_analysis: JobAnalysis, 
        vp_email: SynthesizedEmail, 
        personal_intro: PersonalizedIntro
    ) -> PublishReport:
        """Execute GitHub publishing phase"""
        
        phase_start = time.time()
        
        # Publish to GitHub
        report = await github_publisher_agent.create_and_publish(
            job_analysis=job_analysis,
            vp_email=vp_email,
            personal_intro=personal_intro,
            project_root=os.path.dirname(os.path.abspath(__file__))
        )
        
        phase_time = time.time() - phase_start
        self.execution_metrics["github_publishing_time"] = phase_time
        
        logger.info(f"   ✓ GitHub publishing completed in {phase_time:.1f}s")
        logger.info(f"   ✓ Published {len(report.files_published)} files")
        logger.info(f"   ✓ Repository: {report.repository_url}")
        
        return report
    
    def _calculate_final_metrics(self, results: Dict[str, Any]):
        """Calculate final execution metrics"""
        
        total_time = time.time() - self.start_time
        self.execution_metrics["total_execution_time"] = total_time
        
        # Quality metrics
        job_analysis = results["job_analysis"]
        vp_email = results["vp_email"]  
        personal_intro = results["personal_intro"]
        system_analysis = results["system_analysis"]
        
        self.execution_metrics["quality_metrics"] = {
            "requirements_identified": len(job_analysis.key_requirements),
            "hidden_requirements_found": len(job_analysis.hidden_requirements),
            "vp_voice_alignment": vp_email.voice_alignment_score,
            "intro_job_alignment": personal_intro.alignment_score,
            "intro_voice_authenticity": personal_intro.voice_authenticity_score,
            "overall_system_confidence": system_analysis.overall_confidence
        }
    
    def _print_job_analysis_summary(self, analysis: JobAnalysis):
        """Print job analysis summary"""
        
        print(f"\n📊 JOB ANALYSIS RESULTS:")
        print(f"   Position: {analysis.position_title} at {analysis.company}")
        print(f"   Experience Level: {analysis.experience_level}")
        print(f"   Requirements: {len(analysis.key_requirements)} explicit, {len(analysis.hidden_requirements)} implicit")
        print(f"   Cultural Signals: {len(analysis.company_culture_signals)} detected")
        print(f"   Technical Stack: {', '.join(analysis.technical_stack[:5])}")
    
    def _print_vp_email_summary(self, email: SynthesizedEmail):
        """Print VP email synthesis summary"""
        
        print(f"\n📧 VP EMAIL SYNTHESIS:")
        print(f"   Subject: {email.subject_line}")
        print(f"   Voice Alignment: {email.voice_alignment_score:.1%}")
        print(f"   Confidence: {email.confidence_score:.1%}")
        print(f"   Key Points: {len(email.key_points_covered)} covered")
    
    def _print_intro_summary(self, intro: PersonalizedIntro):
        """Print introduction composition summary"""
        
        print(f"\n✍️  PERSONAL INTRODUCTION:")
        print(f"   Word Count: {intro.total_word_count}")
        print(f"   Job Alignment: {intro.alignment_score:.1%}")
        print(f"   Voice Authenticity: {intro.voice_authenticity_score:.1%}")
        print(f"   Achievements Highlighted: {len(intro.key_achievements_highlighted)}")
    
    def _print_system_analysis_summary(self, analysis: SystemAnalysis):
        """Print system analysis summary"""
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"   Overall Confidence: {analysis.overall_confidence:.1%}")
        print(f"   Decision Points: {len(analysis.decision_points)} analyzed")
        print(f"   Quality Metrics: {len([m for m in analysis.quality_metrics if m.status == 'pass'])} passing")
        print(f"   Success Indicators: {len(analysis.success_indicators)} identified")
    
    def _print_publish_summary(self, report: PublishReport):
        """Print publishing summary"""
        
        print(f"\n📤 GITHUB PUBLISHING:")
        print(f"   Status: {'✅ Success' if report.success else '❌ Failed'}")
        print(f"   Repository: {report.repository_url}")
        print(f"   Files Published: {len(report.files_published)}")
        print(f"   Documentation Score: {report.documentation_quality_score:.1%}")
    
    def _print_success_summary(self, results: Dict[str, Any], verbose: bool):
        """Print final success summary"""
        
        print("\n" + "=" * 60)
        print("🎉 AI AGENT SYSTEM EXECUTION COMPLETE")
        print("=" * 60)
        
        # Time metrics
        total_time = self.execution_metrics["total_execution_time"]
        print(f"⏱️  Total Execution Time: {total_time:.1f} seconds")
        
        # Quality summary
        quality = self.execution_metrics["quality_metrics"]
        print(f"\n📊 QUALITY SUMMARY:")
        print(f"   System Confidence: {quality['overall_system_confidence']:.1%}")
        print(f"   Requirements Analysis: {quality['requirements_identified']} explicit + {quality['hidden_requirements_found']} implicit")
        print(f"   VP Voice Alignment: {quality['vp_voice_alignment']:.1%}")
        print(f"   Introduction Quality: {quality['intro_job_alignment']:.1%} job alignment")
        print(f"   Voice Authenticity: {quality['intro_voice_authenticity']:.1%}")
        
        # File outputs
        print(f"\n📁 GENERATED OUTPUTS:")
        print(f"   Job Analysis: outputs/job_analysis.json")
        print(f"   VP Email: outputs/vp_intro_email.md")
        print(f"   Personal Intro: outputs/personal_intro.md") 
        print(f"   System Analysis: outputs/system_analysis.json")
        print(f"   Decision Transparency: outputs/agent_reasoning.md")
        print(f"   Performance Metrics: outputs/metrics.json")
        
        if "publish_report" in results and results["publish_report"].success:
            print(f"   🌐 GitHub Repository: {results['publish_report'].repository_url}")
        
        print(f"\n💡 This system demonstrates sophisticated AI agent coordination,")
        print(f"   voice synthesis, and automated workflow management -")
        print(f"   core competencies for edge AI development at Analog Devices.")
        
        print("\n🚀 Ready for VP Paul Golding's review!")

def load_job_description(file_path: str) -> str:
    """Load job description from file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Job description file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading job description file: {e}")
        sys.exit(1)

def get_sample_job_description() -> str:
    """Return sample job description if none provided"""
    
    return """
Vibe Coder-in-Residence - Analog Devices

We're seeking an exceptional AI engineer to join our Edge AI team as a Vibe Coder-in-Residence, 
working directly with VP of Edge AI Paul Golding.

This role focuses on developing next-generation AI systems optimized for edge deployment, 
combining deep technical expertise with innovative problem-solving approaches.

Key Responsibilities:
- Architect and implement AI/ML systems for edge computing environments
- Optimize model performance for resource-constrained devices
- Collaborate on strategic AI initiatives and technology roadmaps
- Drive innovation in edge AI deployment and scaling

Requirements:
- 5+ years experience in AI/ML system development
- Proven track record of scaling AI applications
- Experience with multi-model architectures and optimization
- Strong background in system architecture and performance optimization
- Demonstrated ability to work with cross-functional teams
- Passion for pushing the boundaries of what's possible with AI

We offer the opportunity to work on cutting-edge technology that will shape the future of edge AI, 
with direct mentorship from industry leaders and access to world-class resources.

Analog Devices is committed to fostering innovation and providing an environment where 
exceptional engineers can do their best work.
"""

def setup_environment():
    """Setup environment and validate configuration"""
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set up your .env file with API keys")
        sys.exit(1)
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    logger.info("Environment setup complete")

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="AI Agent System for Analog Devices Application",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--job-description", 
        type=str,
        help="Path to job description file (uses sample if not provided)"
    )
    
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish results to GitHub repository"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output with detailed summaries"
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Load job description
    if args.job_description:
        job_description = load_job_description(args.job_description)
        logger.info(f"Loaded job description from {args.job_description}")
    else:
        job_description = get_sample_job_description()
        logger.info("Using sample job description")
    
    # Create orchestrator and run
    orchestrator = AIApplicationOrchestrator()
    
    try:
        # Run the async workflow
        results = asyncio.run(orchestrator.run_complete_workflow(
            job_description=job_description,
            publish_to_github=args.publish,
            verbose=args.verbose
        ))
        
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()