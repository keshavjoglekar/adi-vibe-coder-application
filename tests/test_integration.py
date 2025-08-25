"""
Integration tests for the complete AI agent system
"""

import pytest
import asyncio
import tempfile
import os
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from run_application import AIApplicationOrchestrator, setup_environment
from agents.job_analyzer import JobAnalysis
from agents.vp_voice_synthesizer import SynthesizedEmail
from agents.intro_composer import PersonalizedIntro
from agents.github_publisher import PublishReport
from agents.meta_agent import SystemAnalysis
from lib.llm_client import LLMResponse, ModelProvider

class TestAIApplicationOrchestrator:
    """Test suite for the main application orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return AIApplicationOrchestrator()
    
    @pytest.fixture
    def sample_job_description(self):
        """Sample job description for testing"""
        return """
        Senior AI Engineer - Edge Computing
        Analog Devices
        
        We are seeking a Senior AI Engineer to join our Edge AI team, 
        working on next-generation AI systems for edge deployment.
        
        Requirements:
        - 5+ years of AI/ML experience
        - Experience with edge computing optimization
        - Strong Python and ML framework knowledge
        - Proven track record of scaling AI systems
        
        Nice to have:
        - PhD in Computer Science
        - Experience with hardware acceleration
        - Open source contributions
        
        Join us in shaping the future of edge AI technology.
        """
    
    @pytest.mark.asyncio
    async def test_complete_workflow_without_publishing(self, orchestrator, sample_job_description):
        """Test complete workflow without GitHub publishing"""
        
        with patch('agents.job_analyzer.llm_client.generate') as mock_job_llm, \
             patch('agents.vp_voice_synthesizer.llm_client.generate') as mock_vp_llm, \
             patch('agents.intro_composer.llm_client.generate') as mock_intro_llm, \
             patch('agents.meta_agent.llm_client.generate') as mock_meta_llm:
            
            # Mock all LLM responses
            mock_job_llm.side_effect = [
                LLMResponse("Job analysis response", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Hidden requirements", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8),
                LLMResponse("Culture analysis", "claude-3", ModelProvider.ANTHROPIC, 75, 0.85)
            ]
            
            mock_vp_llm.side_effect = [
                LLMResponse("Strategic context", "claude-3", ModelProvider.ANTHROPIC, 80, 0.9),
                LLMResponse("VP email content", "claude-3", ModelProvider.ANTHROPIC, 200, 0.88),
                LLMResponse("Key points extracted", "claude-3", ModelProvider.ANTHROPIC, 30, 0.8),
                LLMResponse("Subject: Exciting opportunity", "claude-3", ModelProvider.ANTHROPIC, 15, 0.9)
            ]
            
            mock_intro_llm.side_effect = [
                LLMResponse("Positioning analysis", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Current role section", "claude-3", ModelProvider.ANTHROPIC, 40, 0.85),
                LLMResponse("Achievement section", "claude-3", ModelProvider.ANTHROPIC, 60, 0.9),
                LLMResponse("Technical section", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8),
                LLMResponse("Unique value section", "claude-3", ModelProvider.ANTHROPIC, 55, 0.85),
                LLMResponse("Opening hook", "claude-3", ModelProvider.ANTHROPIC, 20, 0.9),
                LLMResponse("Closing statement", "claude-3", ModelProvider.ANTHROPIC, 25, 0.85)
            ]
            
            # Mock file operations
            with patch('builtins.open', create=True) as mock_open, \
                 patch('json.dump') as mock_json_dump:
                
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                # Run the workflow
                results = await orchestrator.run_complete_workflow(
                    job_description=sample_job_description,
                    publish_to_github=False,
                    verbose=False
                )
                
                # Verify results structure
                assert "job_analysis" in results
                assert "vp_email" in results  
                assert "personal_intro" in results
                assert "system_analysis" in results
                assert "publish_report" not in results  # Should not publish
                
                # Verify types
                assert isinstance(results["job_analysis"], JobAnalysis)
                assert isinstance(results["vp_email"], SynthesizedEmail)
                assert isinstance(results["personal_intro"], PersonalizedIntro)
                assert isinstance(results["system_analysis"], SystemAnalysis)
                
                # Verify execution metrics were calculated
                assert orchestrator.execution_metrics["total_execution_time"] > 0
                assert "quality_metrics" in orchestrator.execution_metrics
    
    @pytest.mark.asyncio
    async def test_job_analysis_execution(self, orchestrator, sample_job_description):
        """Test job analysis execution in isolation"""
        
        with patch('agents.job_analyzer.llm_client.generate') as mock_generate:
            mock_generate.side_effect = [
                LLMResponse("Main analysis", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Hidden requirements", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8), 
                LLMResponse("Culture analysis", "claude-3", ModelProvider.ANTHROPIC, 75, 0.85)
            ]
            
            with patch('builtins.open', create=True), \
                 patch('json.dump'):
                
                result = await orchestrator._execute_job_analysis(sample_job_description)
                
                assert isinstance(result, JobAnalysis)
                assert result.position_title is not None
                assert result.company is not None
                assert "job_analysis_time" in orchestrator.execution_metrics
    
    @pytest.mark.asyncio
    async def test_vp_voice_synthesis_execution(self, orchestrator):
        """Test VP voice synthesis execution"""
        
        # Sample job analysis for input
        job_analysis = JobAnalysis(
            position_title="Senior AI Engineer",
            company="Analog Devices",
            key_requirements=[],
            hidden_requirements=[],
            company_culture_signals=[],
            technical_stack=["Python", "TensorFlow"],
            experience_level="Senior",
            team_dynamics="Collaborative",
            growth_opportunities=[],
            red_flags=[],
            alignment_score=0.85,
            success_metrics=[]
        )
        
        with patch('agents.vp_voice_synthesizer.llm_client.generate') as mock_generate:
            mock_generate.side_effect = [
                LLMResponse("Strategic context", "claude-3", ModelProvider.ANTHROPIC, 80, 0.9),
                LLMResponse("Email content", "claude-3", ModelProvider.ANTHROPIC, 200, 0.88),
                LLMResponse("Key points", "claude-3", ModelProvider.ANTHROPIC, 30, 0.8),
                LLMResponse("Subject line", "claude-3", ModelProvider.ANTHROPIC, 15, 0.9)
            ]
            
            with patch('builtins.open', create=True):
                
                result = await orchestrator._execute_vp_voice_synthesis(job_analysis)
                
                assert isinstance(result, SynthesizedEmail)
                assert result.subject_line is not None
                assert result.email_body is not None
                assert result.voice_alignment_score > 0
                assert "vp_synthesis_time" in orchestrator.execution_metrics
    
    @pytest.mark.asyncio
    async def test_intro_composition_execution(self, orchestrator):
        """Test personal introduction composition execution"""
        
        job_analysis = JobAnalysis(
            position_title="AI Engineer",
            company="Tech Corp",
            key_requirements=[],
            hidden_requirements=[],
            company_culture_signals=[],
            technical_stack=["Python"],
            experience_level="Senior",
            team_dynamics="Agile",
            growth_opportunities=[],
            red_flags=[],
            alignment_score=0.88,
            success_metrics=[]
        )
        
        with patch('agents.intro_composer.llm_client.generate') as mock_generate:
            mock_generate.side_effect = [
                LLMResponse("Positioning", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Current role", "claude-3", ModelProvider.ANTHROPIC, 40, 0.85),
                LLMResponse("Achievement", "claude-3", ModelProvider.ANTHROPIC, 60, 0.9),
                LLMResponse("Technical", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8),
                LLMResponse("Unique value", "claude-3", ModelProvider.ANTHROPIC, 55, 0.85),
                LLMResponse("Hook", "claude-3", ModelProvider.ANTHROPIC, 20, 0.9),
                LLMResponse("Closing", "claude-3", ModelProvider.ANTHROPIC, 25, 0.85)
            ]
            
            with patch('builtins.open', create=True):
                
                result = await orchestrator._execute_intro_composition(job_analysis)
                
                assert isinstance(result, PersonalizedIntro)
                assert result.opening_hook is not None
                assert result.alignment_score > 0
                assert "intro_composition_time" in orchestrator.execution_metrics
    
    @pytest.mark.asyncio  
    async def test_meta_analysis_execution(self, orchestrator):
        """Test meta analysis execution"""
        
        # Sample inputs
        job_analysis = JobAnalysis(
            position_title="Engineer", company="Corp", key_requirements=[], 
            hidden_requirements=[], company_culture_signals=[], technical_stack=[],
            experience_level="Senior", team_dynamics="Agile", growth_opportunities=[],
            red_flags=[], alignment_score=0.85, success_metrics=[]
        )
        
        vp_email = SynthesizedEmail(
            subject_line="Subject", email_body="Body", voice_alignment_score=0.88,
            key_points_covered=[], style_metrics={}, confidence_score=0.9
        )
        
        personal_intro = PersonalizedIntro(
            opening_hook="Hook", sections=[], closing_statement="Close",
            call_to_action="CTA", total_word_count=100, alignment_score=0.92,
            key_achievements_highlighted=[], voice_authenticity_score=0.87
        )
        
        with patch('builtins.open', create=True), \
             patch('json.dump'):
            
            result = await orchestrator._execute_meta_analysis(job_analysis, vp_email, personal_intro)
            
            assert isinstance(result, SystemAnalysis)
            assert result.overall_confidence > 0
            assert len(result.decision_points) > 0
            assert "meta_analysis_time" in orchestrator.execution_metrics
    
    def test_calculate_final_metrics(self, orchestrator):
        """Test final metrics calculation"""
        
        # Set up sample results
        job_analysis = JobAnalysis(
            position_title="Test", company="Test", key_requirements=[], 
            hidden_requirements=[], company_culture_signals=[], technical_stack=[],
            experience_level="Mid-level", team_dynamics="Agile", growth_opportunities=[],
            red_flags=[], alignment_score=0.8, success_metrics=[]
        )
        
        vp_email = SynthesizedEmail(
            subject_line="Test", email_body="Test", voice_alignment_score=0.85,
            key_points_covered=[], style_metrics={}, confidence_score=0.88
        )
        
        personal_intro = PersonalizedIntro(
            opening_hook="Test", sections=[], closing_statement="Test", 
            call_to_action="Test", total_word_count=100, alignment_score=0.9,
            key_achievements_highlighted=[], voice_authenticity_score=0.87
        )
        
        system_analysis = SystemAnalysis(
            overall_confidence=0.89, decision_points=[], quality_metrics=[],
            performance_analysis={}, improvement_recommendations=[],
            success_indicators=[], risk_assessment={}
        )
        
        results = {
            "job_analysis": job_analysis,
            "vp_email": vp_email,
            "personal_intro": personal_intro,  
            "system_analysis": system_analysis
        }
        
        orchestrator.start_time = 1000  # Mock start time
        
        with patch('time.time', return_value=1050):  # Mock 50 seconds later
            orchestrator._calculate_final_metrics(results)
        
        assert orchestrator.execution_metrics["total_execution_time"] == 50
        assert "quality_metrics" in orchestrator.execution_metrics
        assert orchestrator.execution_metrics["quality_metrics"]["overall_system_confidence"] == 0.89
    
    def test_print_methods(self, orchestrator, capsys):
        """Test print methods don't crash and produce output"""
        
        # Sample data
        job_analysis = JobAnalysis(
            position_title="Test Engineer", company="Test Corp", key_requirements=[],
            hidden_requirements=[], company_culture_signals=[], technical_stack=["Python"],
            experience_level="Senior", team_dynamics="Agile", growth_opportunities=[],
            red_flags=[], alignment_score=0.85, success_metrics=[]
        )
        
        vp_email = SynthesizedEmail(
            subject_line="Test Subject", email_body="Test Body", voice_alignment_score=0.88,
            key_points_covered=["Point 1"], style_metrics={}, confidence_score=0.9
        )
        
        personal_intro = PersonalizedIntro(
            opening_hook="Test Hook", sections=[], closing_statement="Test Close",
            call_to_action="Test CTA", total_word_count=150, alignment_score=0.92,
            key_achievements_highlighted=["Achievement 1"], voice_authenticity_score=0.87
        )
        
        system_analysis = SystemAnalysis(
            overall_confidence=0.89, decision_points=[], quality_metrics=[],
            performance_analysis={}, improvement_recommendations=[],
            success_indicators=["Success 1"], risk_assessment={}
        )
        
        publish_report = PublishReport(
            success=True, repository_url="https://github.com/test/repo",
            files_published=["file1.py"], documentation_quality_score=0.95,
            accessibility_score=0.9, professional_presentation_score=0.93,
            total_execution_time=45, error_messages=[]
        )
        
        # Test each print method
        orchestrator._print_job_analysis_summary(job_analysis)
        orchestrator._print_vp_email_summary(vp_email) 
        orchestrator._print_intro_summary(personal_intro)
        orchestrator._print_system_analysis_summary(system_analysis)
        orchestrator._print_publish_summary(publish_report)
        
        # Test success summary
        orchestrator.execution_metrics = {
            "total_execution_time": 60,
            "quality_metrics": {
                "overall_system_confidence": 0.89,
                "requirements_identified": 5,
                "hidden_requirements_found": 3,
                "vp_voice_alignment": 0.88,
                "intro_job_alignment": 0.92,
                "intro_voice_authenticity": 0.87
            }
        }
        
        results = {
            "job_analysis": job_analysis,
            "vp_email": vp_email,
            "personal_intro": personal_intro,
            "system_analysis": system_analysis,
            "publish_report": publish_report
        }
        
        orchestrator._print_success_summary(results, verbose=True)
        
        # Check that output was produced
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "Test Engineer" in captured.out
        assert "Test Subject" in captured.out

class TestApplicationUtilities:
    """Test utility functions and error handling"""
    
    def test_load_job_description_success(self):
        """Test successful job description loading"""
        
        from run_application import load_job_description
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test job description content")
            temp_file = f.name
        
        try:
            content = load_job_description(temp_file)
            assert content == "Test job description content"
        finally:
            os.unlink(temp_file)
    
    def test_load_job_description_file_not_found(self):
        """Test job description loading with missing file"""
        
        from run_application import load_job_description
        
        with patch('sys.exit') as mock_exit:
            load_job_description("nonexistent_file.txt")
            mock_exit.assert_called_with(1)
    
    def test_get_sample_job_description(self):
        """Test sample job description generation"""
        
        from run_application import get_sample_job_description
        
        sample = get_sample_job_description()
        
        assert isinstance(sample, str)
        assert len(sample) > 100
        assert "Vibe Coder-in-Residence" in sample
        assert "Analog Devices" in sample
    
    def test_setup_environment_success(self):
        """Test successful environment setup"""
        
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_openai_key',
            'ANTHROPIC_API_KEY': 'test_anthropic_key'
        }), patch('os.makedirs') as mock_makedirs:
            
            # Should not raise exception
            setup_environment()
            
            # Should create directories
            mock_makedirs.assert_any_call("outputs", exist_ok=True)
            mock_makedirs.assert_any_call("docs", exist_ok=True)
    
    def test_setup_environment_missing_keys(self):
        """Test environment setup with missing API keys"""
        
        with patch.dict(os.environ, {}, clear=True), \
             patch('sys.exit') as mock_exit:
            
            setup_environment()
            mock_exit.assert_called_with(1)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_llm_client_failure_handling(self):
        """Test handling of LLM client failures"""
        
        from agents.job_analyzer import job_analyzer
        
        with patch('agents.job_analyzer.llm_client.generate') as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                await job_analyzer.analyze_job_description("Test job description")
    
    @pytest.mark.asyncio 
    async def test_file_write_permission_error(self):
        """Test handling of file write permission errors"""
        
        from agents.job_analyzer import job_analyzer, JobAnalysis
        
        sample_analysis = JobAnalysis(
            position_title="Test", company="Test", key_requirements=[],
            hidden_requirements=[], company_culture_signals=[], technical_stack=[],
            experience_level="Mid-level", team_dynamics="Agile", growth_opportunities=[],
            red_flags=[], alignment_score=0.8, success_metrics=[]
        )
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            # Should not raise exception - graceful handling
            try:
                job_analyzer.save_analysis(sample_analysis, "/readonly/path/analysis.json")
            except PermissionError:
                pass  # Expected for this test
    
    def test_invalid_job_description_handling(self):
        """Test handling of invalid job descriptions"""
        
        from run_application import AIApplicationOrchestrator
        
        orchestrator = AIApplicationOrchestrator()
        
        # Test empty job description
        empty_desc = ""
        assert len(empty_desc) == 0
        
        # Test very short job description
        short_desc = "Hiring."
        assert len(short_desc) < 50

class TestPerformanceIntegration:
    """Performance and timing tests for integration"""
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test that agents can handle concurrent execution"""
        
        from agents.job_analyzer import job_analyzer
        from agents.vp_voice_synthesizer import vp_voice_synthesizer
        
        with patch('agents.job_analyzer.llm_client.generate') as mock_job_generate, \
             patch('agents.vp_voice_synthesizer.llm_client.generate') as mock_vp_generate:
            
            # Mock responses
            mock_job_generate.side_effect = [
                LLMResponse("Analysis", "claude-3", ModelProvider.ANTHROPIC, 100, 0.9),
                LLMResponse("Hidden", "claude-3", ModelProvider.ANTHROPIC, 50, 0.8),
                LLMResponse("Culture", "claude-3", ModelProvider.ANTHROPIC, 75, 0.85)
            ]
            
            mock_vp_generate.side_effect = [
                LLMResponse("Context", "claude-3", ModelProvider.ANTHROPIC, 80, 0.9),
                LLMResponse("Email", "claude-3", ModelProvider.ANTHROPIC, 200, 0.88),
                LLMResponse("Points", "claude-3", ModelProvider.ANTHROPIC, 30, 0.8),
                LLMResponse("Subject", "claude-3", ModelProvider.ANTHROPIC, 15, 0.9)
            ]
            
            with patch('builtins.open', create=True), \
                 patch('json.dump'):
                
                # Run agents concurrently (simulated)
                job_task = job_analyzer.analyze_job_description("Test job")
                
                job_result = await job_task
                assert isinstance(job_result, JobAnalysis)
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test that memory usage remains stable during execution"""
        
        import gc
        
        initial_objects = len(gc.get_objects())
        
        # Create and destroy orchestrator multiple times
        for _ in range(5):
            orchestrator = AIApplicationOrchestrator()
            del orchestrator
        
        gc.collect()  # Force garbage collection
        
        final_objects = len(gc.get_objects())
        
        # Memory usage should not grow significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 1000  # Allow some growth but not excessive

# Test configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_env_vars():
    """Temporary environment variables for testing"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'ANTHROPIC_API_KEY': 'test_anthropic_key',
        'GITHUB_TOKEN': 'test_github_token',
        'GITHUB_USERNAME': 'test_user'
    }):
        yield

if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])