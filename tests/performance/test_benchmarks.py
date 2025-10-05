"""
Performance benchmark tests
"""
import pytest
from unittest.mock import Mock, patch
from gcp.gemini_service import GeminiService


@pytest.mark.benchmark
class TestGeminiServicePerformance:
    """Performance benchmarks for Gemini services"""
    
    @pytest.fixture
    def gemini_service(self):
        """Create mocked GeminiService"""
        with patch('gcp.gemini_service.genai.Client'):
            return GeminiService(project_id='test-project')
    
    @pytest.mark.asyncio
    async def test_writing_evaluation_performance(self, benchmark, gemini_service):
        """Benchmark writing evaluation performance"""
        import json
        
        mock_response = Mock()
        mock_response.text = json.dumps({
            "overall_band": 7.0,
            "task_achievement": {"score": 7.0, "strengths": [], "weaknesses": []},
            "coherence_cohesion": {"score": 7.0, "strengths": [], "weaknesses": []},
            "lexical_resource": {"score": 7.0, "strengths": [], "weaknesses": []},
            "grammatical_range_accuracy": {"score": 7.0, "strengths": [], "weaknesses": []}
        })
        
        gemini_service.client.models.generate_content = Mock(return_value=mock_response)
        
        async def evaluate():
            return await gemini_service.evaluate_writing_task(
                task_type='academic_task1',
                task_prompt='Test prompt',
                student_response='Test response' * 50,
                word_count=150
            )
        
        result = benchmark(lambda: pytest.importorskip('asyncio').run(evaluate()))
        assert result['overall_band'] == 7.0
    
    def test_prompt_generation_performance(self, benchmark, gemini_service):
        """Benchmark prompt generation performance"""
        
        def generate_prompt():
            return gemini_service._get_writing_evaluation_prompt(
                'academic_task1',
                'Test prompt',
                'Test response' * 100,
                150
            )
        
        result = benchmark(generate_prompt)
        assert len(result) > 1000  # Prompt should be substantial
