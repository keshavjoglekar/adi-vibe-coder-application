"""
Comprehensive test suite for all AI agents
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import asdict

from agents.job_analyzer import job_analyzer, JobAnalysis, JobRequirement
from agents.vp_voice_synthesizer import vp_voice_synthesizer, SynthesizedEmail
from agents.intro_composer import intro_composer, PersonalizedIntro
from agents.github_publisher import github_publisher_agent, PublishReport
from agents.meta_agent import meta_agent, SystemAnalysis
from lib.llm_client import llm_client, LLMResponse, ModelProvider

class TestJobAnalyzer:
    """Test suite for Job Analyzer Agent"""
    
    @pytest.fixture
    def sample_job_description(self):
        return """
        Senior AI Engineer - Edge Computing
        
        We are seeking a Senior AI Engineer to join our Edge AI team.
        
        Requirements:
        - 5+ years of experience in AI/ML development
        - Experience with edge computing and optimization
        - Strong Python programming skills
        - Knowledge of TensorFlow or PyTorch
        - Experience with distributed systems
        
        Nice to have:
        - PhD in Computer Science or related field
        - Experience with hardware acceleration
        - Open source contributions
        """
    
    @pytest.mark.asyncio
    async def test_analyze_job_description(self, sample_job_description):
        """Test basic job description analysis"""
        
        with patch.object(llm_client, 'generate') as mock_generate:
            # Mock LLM responses
            mock_generate.side_effect = [
                LLMResponse("Analysis response", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Hidden requirements", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8),
                LLMResponse("Culture analysis", "claude-3", ModelProvider.ANTHROPIC, 75, 0.85)
            ]
            
            with patch.object(job_analyzer, '_structure_analysis') as mock_structure:
                mock_analysis = JobAnalysis(
                    position_title="Senior AI Engineer",
                    company="Test Company",
                    key_requirements=[
                        JobRequirement("technical", "Python programming", "critical", "Code samples", 0.9),
                        JobRequirement("experience", "5+ years AI/ML", "critical", "Resume", 0.85)
                    ],
                    hidden_requirements=["Collaboration skills", "Problem-solving"],
                    company_culture_signals=["Innovation-focused", "Technical excellence"],
                    technical_stack=["Python", "TensorFlow", "PyTorch"],
                    experience_level="Senior",
                    team_dynamics="Collaborative",
                    growth_opportunities=["Technical leadership"],
                    red_flags=[],
                    alignment_score=0.85,
                    success_metrics=["Project delivery", "Code quality"]
                )
                mock_structure.return_value = mock_analysis
                
                result = await job_analyzer.analyze_job_description(sample_job_description)
                
                assert isinstance(result, JobAnalysis)
                assert result.position_title == "Senior AI Engineer"
                assert len(result.key_requirements) == 2
                assert result.alignment_score == 0.85
    
    def test_extract_position_title(self):
        """Test position title extraction"""
        
        job_desc = "Senior AI Engineer - Edge Computing\n\nWe are hiring for..."
        title = job_analyzer._extract_position_title(job_desc)
        assert "Senior AI Engineer" in title
    
    def test_extract_technical_stack(self):
        """Test technical stack extraction"""
        
        job_desc = "Requirements: Python, TensorFlow, PyTorch, Docker, Kubernetes"
        stack = job_analyzer._extract_technical_stack(job_desc)
        
        assert "Python" in stack
        assert "TensorFlow" in stack
        assert "Docker" in stack
    
    def test_determine_experience_level(self):
        """Test experience level determination"""
        
        # Test senior level
        job_desc = "5+ years of experience in AI/ML"
        level = job_analyzer._determine_experience_level(job_desc)
        assert level == "Mid-level"
        
        # Test junior level  
        job_desc = "1-2 years of experience"
        level = job_analyzer._determine_experience_level(job_desc)
        assert level == "Junior"

class TestVPVoiceSynthesizer:
    """Test suite for VP Voice Synthesizer Agent"""
    
    @pytest.fixture
    def sample_job_analysis(self):
        return JobAnalysis(
            position_title="VP of Engineering",
            company="Tech Corp",
            key_requirements=[
                JobRequirement("leadership", "Team management", "critical", "References", 0.9)
            ],
            hidden_requirements=["Strategic thinking"],
            company_culture_signals=["Innovation"], 
            technical_stack=["Python"],
            experience_level="Executive",
            team_dynamics="Leadership",
            growth_opportunities=["Strategic impact"],
            red_flags=[],
            alignment_score=0.88,
            success_metrics=["Team growth"]
        )
    
    @pytest.fixture
    def sample_candidate_background(self):
        return {
            "name": "Test Candidate",
            "current_role": "Senior Engineer",
            "key_achievement": "Scaled system 10x"
        }
    
    @pytest.mark.asyncio
    async def test_generate_intro_email(self, sample_job_analysis, sample_candidate_background):
        """Test VP introduction email generation"""
        
        with patch.object(llm_client, 'generate') as mock_generate:
            mock_generate.side_effect = [
                LLMResponse("Strategic context", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Email content", "claude-3", ModelProvider.ANTHROPIC, 200, 0.85),
                LLMResponse("Key points", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8),
                LLMResponse("Subject: Great opportunity", "claude-3", ModelProvider.ANTHROPIC, 20, 0.9)
            ]
            
            result = await vp_voice_synthesizer.generate_intro_email(
                job_analysis=sample_job_analysis,
                candidate_background=sample_candidate_background
            )
            
            assert isinstance(result, SynthesizedEmail)
            assert result.subject_line is not None
            assert result.email_body is not None
            assert result.confidence_score > 0
    
    def test_voice_profile_formatting(self):
        """Test voice profile formatting"""
        
        formatted = vp_voice_synthesizer._format_voice_profile()
        assert "VOICE CHARACTERISTICS:" in formatted
        assert "double dashes" in formatted.lower()
        assert "technical depth" in formatted.lower()
    
    @pytest.mark.asyncio
    async def test_validate_voice_alignment(self):
        """Test voice alignment validation"""
        
        # Test content with Paul Golding characteristics
        content_with_patterns = "This approach -- which leverages our technical architecture -- enables strategic transformation."
        score = await vp_voice_synthesizer._validate_voice_alignment(content_with_patterns)
        assert score > 0.5
        
        # Test content without patterns
        basic_content = "Thank you for your interest. We will be in touch soon."
        score = await vp_voice_synthesizer._validate_voice_alignment(basic_content)
        assert score >= 0

class TestIntroComposer:
    """Test suite for Introduction Composer Agent"""
    
    @pytest.fixture
    def sample_job_analysis(self):
        return JobAnalysis(
            position_title="AI Engineer", 
            company="AI Corp",
            key_requirements=[
                JobRequirement("technical", "AI/ML experience", "critical", "Projects", 0.9),
                JobRequirement("experience", "Scale experience", "important", "Metrics", 0.8)
            ],
            hidden_requirements=["Innovation mindset"],
            company_culture_signals=["Technical excellence"],
            technical_stack=["Python", "TensorFlow"],
            experience_level="Senior",
            team_dynamics="Collaborative", 
            growth_opportunities=["Technical leadership"],
            red_flags=[],
            alignment_score=0.85,
            success_metrics=["Impact metrics"]
        )
    
    @pytest.mark.asyncio
    async def test_compose_introduction(self, sample_job_analysis):
        """Test personal introduction composition"""
        
        with patch.object(llm_client, 'generate') as mock_generate:
            mock_generate.side_effect = [
                LLMResponse("Positioning analysis", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Current role content", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8),
                LLMResponse("Achievement content", "claude-3", ModelProvider.ANTHROPIC, 80, 0.85),
                LLMResponse("Technical content", "claude-3", ModelProvider.ANTHROPIC, 60, 0.8),
                LLMResponse("Unique value content", "claude-3", ModelProvider.ANTHROPIC, 70, 0.85),
                LLMResponse("Opening hook", "claude-3", ModelProvider.ANTHROPIC, 25, 0.9),
                LLMResponse("Closing statement", "claude-3", ModelProvider.ANTHROPIC, 30, 0.85)
            ]
            
            result = await intro_composer.compose_introduction(sample_job_analysis)
            
            assert isinstance(result, PersonalizedIntro)
            assert result.opening_hook is not None
            assert len(result.sections) > 0
            assert result.total_word_count > 0
            assert result.alignment_score > 0
    
    def test_select_relevant_metrics(self, sample_job_analysis):
        """Test relevant metrics selection"""
        
        positioning_strategy = {"primary_angle": "Scale expert"}
        relevant_metrics = intro_composer._select_relevant_metrics(sample_job_analysis, positioning_strategy)
        
        assert isinstance(relevant_metrics, list)
        assert len(relevant_metrics) > 0
    
    def test_template_selection(self, sample_job_analysis):
        """Test introduction template selection"""
        
        positioning_strategy = {"primary_angle": "Technical leader"}
        template = intro_composer._select_template(positioning_strategy, sample_job_analysis)
        
        assert template in ["technical_leader", "scale_expert", "ai_innovator", "cost_optimizer"]

class TestGitHubPublisher:
    """Test suite for GitHub Publisher Agent"""
    
    @pytest.fixture
    def sample_job_analysis(self):
        return JobAnalysis(
            position_title="Software Engineer",
            company="GitHub Corp", 
            key_requirements=[],
            hidden_requirements=[],
            company_culture_signals=[],
            technical_stack=[],
            experience_level="Mid-level",
            team_dynamics="Agile",
            growth_opportunities=[], 
            red_flags=[],
            alignment_score=0.8,
            success_metrics=[]
        )
    
    @pytest.fixture
    def sample_vp_email(self):
        return SynthesizedEmail(
            subject_line="Great opportunity",
            email_body="Email content here",
            voice_alignment_score=0.85,
            key_points_covered=["Point 1", "Point 2"],
            style_metrics={"score": 0.8},
            confidence_score=0.88
        )
    
    @pytest.fixture
    def sample_personal_intro(self):
        return PersonalizedIntro(
            opening_hook="Hook here",
            sections=[],
            closing_statement="Closing here", 
            call_to_action="CTA here",
            total_word_count=150,
            alignment_score=0.9,
            key_achievements_highlighted=["Achievement 1"],
            voice_authenticity_score=0.85
        )
    
    @pytest.mark.asyncio
    async def test_create_publish_plan(self, sample_job_analysis, sample_vp_email, sample_personal_intro):
        """Test publishing plan creation"""
        
        plan = await github_publisher_agent._create_publish_plan(
            sample_job_analysis, sample_vp_email, sample_personal_intro
        )
        
        assert plan.repository_name == "adi-vibe-coder-application"
        assert "GitHub Corp" in plan.repository_description
        assert len(plan.key_features) > 0
    
    @pytest.mark.asyncio
    async def test_generate_output_files(self, sample_job_analysis, sample_vp_email, sample_personal_intro):
        """Test output file generation"""
        
        output_files = await github_publisher_agent._generate_output_files(
            sample_job_analysis, sample_vp_email, sample_personal_intro
        )
        
        assert "outputs/job_analysis.json" in output_files
        assert "outputs/vp_intro_email.md" in output_files  
        assert "outputs/personal_intro.md" in output_files
        assert "outputs/metrics.json" in output_files
        
        # Test JSON validity
        job_analysis_json = json.loads(output_files["outputs/job_analysis.json"])
        assert job_analysis_json["position_title"] == "Software Engineer"

class TestMetaAgent:
    """Test suite for Meta Agent"""
    
    @pytest.fixture
    def sample_system_outputs(self):
        job_analysis = JobAnalysis(
            position_title="Test Role",
            company="Test Corp",
            key_requirements=[JobRequirement("tech", "Python", "critical", "Code", 0.9)],
            hidden_requirements=["Teamwork"], 
            company_culture_signals=["Innovation"],
            technical_stack=["Python"],
            experience_level="Senior",
            team_dynamics="Agile",
            growth_opportunities=["Leadership"],
            red_flags=[],
            alignment_score=0.85,
            success_metrics=["Quality"]
        )
        
        vp_email = SynthesizedEmail(
            subject_line="Test Subject",
            email_body="Test body",
            voice_alignment_score=0.88,
            key_points_covered=["Point 1"],
            style_metrics={"double_dash_usage": 2},
            confidence_score=0.9
        )
        
        personal_intro = PersonalizedIntro(
            opening_hook="Test hook",
            sections=[],
            closing_statement="Test closing",
            call_to_action="Test CTA", 
            total_word_count=100,
            alignment_score=0.92,
            key_achievements_highlighted=["Achievement"],
            voice_authenticity_score=0.87
        )
        
        return job_analysis, vp_email, personal_intro
    
    @pytest.mark.asyncio
    async def test_analyze_system_performance(self, sample_system_outputs):
        """Test comprehensive system performance analysis"""
        
        job_analysis, vp_email, personal_intro = sample_system_outputs
        
        analysis = await meta_agent.analyze_system_performance(
            job_analysis, vp_email, personal_intro
        )
        
        assert isinstance(analysis, SystemAnalysis)
        assert analysis.overall_confidence > 0
        assert len(analysis.decision_points) > 0
        assert len(analysis.quality_metrics) > 0
        assert len(analysis.improvement_recommendations) > 0
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation"""
        
        from agents.meta_agent import QualityMetric, DecisionPoint
        from datetime import datetime
        
        quality_metrics = [
            QualityMetric("Test 1", 0.9, 0.8, "pass", "Good"),
            QualityMetric("Test 2", 0.85, 0.8, "pass", "Good")
        ]
        
        decision_points = [
            DecisionPoint("Agent1", "Decision1", "Choice", "Reason", 0.88, [], [], datetime.now().isoformat()),
            DecisionPoint("Agent2", "Decision2", "Choice", "Reason", 0.92, [], [], datetime.now().isoformat())
        ]
        
        confidence = meta_agent._calculate_overall_confidence(quality_metrics, decision_points)
        
        assert 0 <= confidence <= 1
        assert confidence > 0.8  # Should be high given good inputs
    
    def test_identify_success_indicators(self, sample_system_outputs):
        """Test success indicator identification"""
        
        job_analysis, vp_email, personal_intro = sample_system_outputs
        
        indicators = meta_agent._identify_success_indicators(job_analysis, vp_email, personal_intro)
        
        assert isinstance(indicators, list)
        assert len(indicators) > 0

class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        
        # This test would require actual API keys and would be expensive
        # In practice, this would be run in a separate test suite or CI/CD pipeline
        # with proper API mocking or test API keys
        pass
    
    def test_data_flow_consistency(self):
        """Test that data flows correctly between agents"""
        
        # Test that JobAnalysis output is compatible with other agents
        sample_analysis = JobAnalysis(
            position_title="Test",
            company="Test",
            key_requirements=[],
            hidden_requirements=[],
            company_culture_signals=[], 
            technical_stack=[],
            experience_level="Senior",
            team_dynamics="Agile",
            growth_opportunities=[],
            red_flags=[],
            alignment_score=0.8,
            success_metrics=[]
        )
        
        # Should be serializable
        serialized = asdict(sample_analysis)
        assert isinstance(serialized, dict)
        assert serialized["position_title"] == "Test"

# Fixtures and utilities
@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return LLMResponse(
        content="Mock response content",
        model="claude-3-sonnet-20240229", 
        provider=ModelProvider.ANTHROPIC,
        tokens_used=100,
        confidence_score=0.85
    )

@pytest.fixture
def mock_async_llm_generate(mock_llm_response):
    """Mock async LLM generate function"""
    return AsyncMock(return_value=mock_llm_response)

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Performance tests
class TestPerformance:
    """Performance and load tests"""
    
    def test_memory_usage(self):
        """Test memory usage stays within reasonable bounds"""
        import sys
        
        # Simple memory check - in production would use memory_profiler
        initial_objects = len(list(sys.modules.keys()))
        
        # Import all modules
        from agents import job_analyzer, vp_voice_synthesizer, intro_composer
        
        final_objects = len(list(sys.modules.keys()))
        
        # Should not import excessive modules
        assert (final_objects - initial_objects) < 50
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test that operations complete within reasonable time"""
        
        # Mock a slow operation
        with patch.object(llm_client, 'generate') as mock_generate:
            # Simulate delay
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(0.1)  # Short delay for testing
                return LLMResponse("response", "model", ModelProvider.ANTHROPIC, 100, 0.8)
            
            mock_generate.side_effect = slow_response
            
            start_time = asyncio.get_event_loop().time()
            
            # This should complete quickly in tests
            with patch.object(job_analyzer, '_structure_analysis') as mock_structure:
                mock_structure.return_value = JobAnalysis(
                    position_title="Test",
                    company="Test", 
                    key_requirements=[],
                    hidden_requirements=[],
                    company_culture_signals=[],
                    technical_stack=[], 
                    experience_level="Mid-level",
                    team_dynamics="Agile",
                    growth_opportunities=[],
                    red_flags=[],
                    alignment_score=0.8,
                    success_metrics=[]
                )
                
                await job_analyzer.analyze_job_description("Sample job description")
            
            duration = asyncio.get_event_loop().time() - start_time
            assert duration < 5.0  # Should complete within 5 seconds

if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_agents.py -v
    pytest.main([__file__, "-v"])