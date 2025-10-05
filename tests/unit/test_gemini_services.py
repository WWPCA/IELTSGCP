"""
Unit tests for Gemini AI services
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from gcp.gemini_service import GeminiService
from gcp.gemini_live_service import GeminiLiveService


class TestGeminiService:
    """Test suite for GeminiService"""
    
    @pytest.fixture
    def gemini_service(self):
        """Create GeminiService instance"""
        with patch('gcp.gemini_service.genai.Client'):
            service = GeminiService(project_id='test-project', region='us-central1')
            return service
    
    @pytest.mark.asyncio
    async def test_evaluate_writing_task_academic_task1(self, gemini_service):
        """Test writing evaluation for Academic Task 1"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "overall_band": 7.0,
            "band_prediction": "Band 7.0 - Good User",
            "task_achievement": {"score": 7.0, "strengths": [], "weaknesses": []},
            "coherence_cohesion": {"score": 7.0, "strengths": [], "weaknesses": []},
            "lexical_resource": {"score": 7.0, "strengths": [], "weaknesses": []},
            "grammatical_range_accuracy": {"score": 7.0, "strengths": [], "weaknesses": []}
        })
        
        gemini_service.client.models.generate_content = Mock(return_value=mock_response)
        
        result = await gemini_service.evaluate_writing_task(
            task_type='academic_task1',
            task_prompt='Describe the graph',
            student_response='The graph shows...',
            word_count=150
        )
        
        assert result['overall_band'] == 7.0
        assert result['band_prediction'] == "Band 7.0 - Good User"
        assert 'task_achievement' in result
    
    @pytest.mark.asyncio
    async def test_evaluate_writing_task_general_task2(self, gemini_service):
        """Test writing evaluation for General Task 2"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "overall_band": 6.5,
            "band_prediction": "Band 6.5 - Competent User",
            "task_response": {"score": 6.5, "strengths": [], "weaknesses": []},
            "coherence_cohesion": {"score": 6.5, "strengths": [], "weaknesses": []},
            "lexical_resource": {"score": 6.5, "strengths": [], "weaknesses": []},
            "grammatical_range_accuracy": {"score": 6.5, "strengths": [], "weaknesses": []}
        })
        
        gemini_service.client.models.generate_content = Mock(return_value=mock_response)
        
        result = await gemini_service.evaluate_writing_task(
            task_type='general_task2',
            task_prompt='Write an essay...',
            student_response='In my opinion...',
            word_count=250
        )
        
        assert result['overall_band'] == 6.5
        assert 'task_response' in result
    
    def test_writing_evaluation_prompt_structure(self, gemini_service):
        """Test that evaluation prompts contain official IELTS criteria"""
        prompt = gemini_service._get_writing_evaluation_prompt(
            'academic_task1',
            'Test prompt',
            'Test response',
            150
        )
        
        assert 'Band 9' in prompt
        assert 'Band 7-8' in prompt
        assert 'Band 5-6' in prompt
        assert 'Task Achievement' in prompt or 'Task Response' in prompt
        assert 'Coherence and Cohesion' in prompt
        assert 'Lexical Resource' in prompt
        assert 'Grammatical Range and Accuracy' in prompt
        assert 'personalized_improvement_plan' in prompt


class TestGeminiLiveService:
    """Test suite for GeminiLiveService"""
    
    @pytest.fixture
    def gemini_live_service(self):
        """Create GeminiLiveService instance"""
        with patch('gcp.gemini_live_service.genai.Client'):
            service = GeminiLiveService(project_id='test-project', region='us-central1')
            return service
    
    def test_maya_system_prompt_contains_band_descriptors(self, gemini_live_service):
        """Test Maya's system prompt contains official IELTS band descriptors"""
        prompt = gemini_live_service.get_maya_system_prompt('speaking')
        
        assert 'Band 9' in prompt
        assert 'Band 7-8' in prompt
        assert 'Band 5-6' in prompt
        assert 'Fluency and Coherence' in prompt
        assert 'Lexical Resource' in prompt
        assert 'Grammatical Range and Accuracy' in prompt
        assert 'Pronunciation' in prompt
    
    def test_maya_system_prompt_speaking_parts(self, gemini_live_service):
        """Test Maya's prompts for different speaking parts"""
        part1 = gemini_live_service.get_maya_system_prompt('speaking_part1')
        part2 = gemini_live_service.get_maya_system_prompt('speaking_part2')
        part3 = gemini_live_service.get_maya_system_prompt('speaking_part3')
        
        assert 'PART 1' in part1
        assert 'PART 2' in part2
        assert 'PART 3' in part3
    
    @pytest.mark.asyncio
    async def test_generate_assessment_feedback(self, gemini_live_service):
        """Test speaking assessment feedback generation"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "overall_band": 7.5,
            "band_prediction": "Band 7.5 - Good User",
            "fluency_coherence": {
                "score": 7.5,
                "band_descriptor": "Band 7-8",
                "strengths": ["Speaks at length", "Good discourse markers"],
                "areas_for_improvement": ["Occasional hesitation"]
            },
            "personalized_improvement_plan": {
                "focus_areas": [],
                "immediate_actions": [],
                "weekly_practice_schedule": {},
                "target_overall_band": 8.0,
                "estimated_timeline": "4-6 weeks"
            }
        })
        
        gemini_live_service.client.models.generate_content = Mock(return_value=mock_response)
        
        result = await gemini_live_service.generate_assessment_feedback(
            transcript="Maya: Hello. Student: Hi...",
            assessment_type='speaking'
        )
        
        assert result['overall_band'] == 7.5
        assert 'personalized_improvement_plan' in result
        assert 'focus_areas' in result['personalized_improvement_plan']
