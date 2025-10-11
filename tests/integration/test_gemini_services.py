"""
Integration tests for Gemini AI services with real API calls
"""
import pytest
import os
from gcp.gemini_service import GeminiService
from gcp.gemini_live_service import GeminiLiveService


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('GEMINI_API_KEY') or not os.getenv('GOOGLE_CLOUD_PROJECT'),
    reason="GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT not set - skipping integration tests"
)
class TestGeminiServiceIntegration:
    """Integration tests for GeminiService with real API"""
    
    @pytest.fixture
    def gemini_service(self):
        """Create GeminiService with real credentials"""
        return GeminiService(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            region='us-central1'
        )
    
    @pytest.mark.asyncio
    async def test_real_writing_evaluation_academic_task1(self, gemini_service):
        """Test real API call for Academic Task 1 writing evaluation"""
        task_prompt = """The graph below shows the number of tourists visiting a Caribbean island between 2010 and 2017.

Summarize the information by selecting and reporting the main features and make comparisons where relevant."""
        
        student_response = """The line graph illustrates the trends in tourist arrivals at a Caribbean island from 2010 to 2017, distinguishing between those who stayed on the island and those who stayed on cruise ships.

Overall, total tourist numbers increased significantly over the period, with visitors staying on cruise ships showing more dramatic growth than those staying on the island.

In 2010, approximately 0.75 million tourists stayed on the island, while only about 0.25 million stayed on cruise ships. Both categories showed steady growth until 2015-2016. Island-staying tourists peaked at around 1.5 million in 2013 before fluctuating and ending at approximately 1.5 million in 2017.

In contrast, cruise ship tourists experienced more consistent growth, rising from 0.25 million in 2010 to approximately 2 million by 2017, overtaking island-staying tourists around 2015. By the end of the period, the total number of visitors reached approximately 3.5 million, with cruise ship tourists representing the majority."""
        
        result = await gemini_service.evaluate_writing_task(
            task_type='academic_task1',
            task_prompt=task_prompt,
            student_response=student_response,
            word_count=len(student_response.split())
        )
        
        # Assertions - Basic structure
        assert 'overall_band' in result
        assert 0 <= result['overall_band'] <= 9
        assert 'band_prediction' in result
        
        # All 4 IELTS criteria present
        assert 'task_achievement' in result
        assert 'coherence_cohesion' in result
        assert 'lexical_resource' in result
        assert 'grammatical_range_accuracy' in result
        
        # Detailed feedback components
        assert 'personalized_improvement_plan' in result
        improvement_plan = result['personalized_improvement_plan']
        assert 'focus_areas' in improvement_plan
        assert 'immediate_actions' in improvement_plan
        assert 'study_schedule' in improvement_plan
        assert 'target_overall_band' in improvement_plan
        assert 'estimated_timeline' in improvement_plan
        assert 'progress_tracking' in improvement_plan
        
        # Sample improvements present
        assert 'sample_improvements' in result
        assert len(result['sample_improvements']) > 0
        
        # Performance summary
        assert 'performance_summary' in result
        assert 'strongest_criterion' in result['performance_summary']
        assert 'weakest_criterion' in result['performance_summary']
    
    @pytest.mark.asyncio
    async def test_real_writing_evaluation_general_task2(self, gemini_service):
        """Test real API call for General Task 2 writing evaluation"""
        task_prompt = """Some people think that children should begin their formal education at a very early age. Others think they should begin after 7 years of age. Discuss both views and give your own opinion."""
        
        student_response = """There is ongoing debate about the optimal age for children to start formal education. While some argue for early enrollment, others believe children should wait until after age 7. This essay will discuss both perspectives and provide my opinion.

Proponents of early formal education argue that young children's brains are highly adaptable and can absorb information quickly. Early exposure to structured learning environments can develop cognitive skills and social abilities from a tender age. Additionally, working parents often require childcare, and formal education can provide a productive solution.

However, others contend that children under 7 benefit more from play-based learning rather than formal instruction. Research suggests that premature academic pressure can diminish creativity and cause stress. Countries like Finland, which begin formal schooling at age 7, consistently rank highly in educational outcomes, suggesting that delayed formal education doesn't hinder academic achievement.

In my opinion, a balanced approach is ideal. While very young children may not need rigorous academic instruction, introducing structured learning through play-based methods can be beneficial. Formal education could begin around age 6, allowing children to develop socially and emotionally while gradually transitioning to academic learning.

In conclusion, both early and delayed formal education have merits. A moderate approach that combines play-based learning with gradual academic introduction appears most beneficial for children's holistic development."""
        
        result = await gemini_service.evaluate_writing_task(
            task_type='general_task2',
            task_prompt=task_prompt,
            student_response=student_response,
            word_count=len(student_response.split())
        )
        
        # Assertions - Basic structure
        assert result['overall_band'] >= 6.0
        assert 'task_response' in result
        
        # Comprehensive improvement plan
        improvement_plan = result['personalized_improvement_plan']
        assert 'focus_areas' in improvement_plan
        assert 'immediate_actions' in improvement_plan
        assert 'study_schedule' in improvement_plan
        assert 'writing_exercises' in improvement_plan
        assert 'target_overall_band' in improvement_plan
        assert 'estimated_timeline' in improvement_plan
        
        # Verify focus areas have required fields
        if len(improvement_plan['focus_areas']) > 0:
            focus_area = improvement_plan['focus_areas'][0]
            assert 'criterion' in focus_area
            assert 'current_band' in focus_area
            assert 'target_band' in focus_area
            assert 'practice_activities' in focus_area
            assert 'estimated_time' in focus_area


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('GEMINI_API_KEY') or not os.getenv('GOOGLE_CLOUD_PROJECT'),
    reason="GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT not set - skipping integration tests"
)
class TestGeminiLiveServiceIntegration:
    """Integration tests for GeminiLiveService with real API"""
    
    @pytest.fixture
    def gemini_live_service(self):
        """Create GeminiLiveService with real credentials"""
        return GeminiLiveService(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            region='us-central1'
        )
    
    @pytest.mark.asyncio
    async def test_real_speaking_feedback_generation(self, gemini_live_service):
        """Test real API call for speaking assessment feedback"""
        transcript = """Maya: Hello, my name is Maya. Could you please tell me your full name?
Student: My name is John Smith.
Maya: Thank you. Now let's talk about your hometown. Where are you from?
Student: I'm from London, England. It's a large city in the southeast of the country.
Maya: What do you like most about your hometown?
Student: Well, I really enjoy the cultural diversity. There are so many different restaurants, museums, and cultural events. You can experience food and traditions from all over the world without leaving the city. Also, the public transportation system is excellent, which makes it easy to get around.
Maya: Do you think you will continue living there in the future?
Student: Probably not permanently. While I love London, it's quite expensive and very crowded. I think in the future I might prefer living in a smaller town or maybe even in the countryside, somewhere more peaceful but still close enough to visit London regularly."""
        
        result = await gemini_live_service.generate_assessment_feedback(
            transcript=transcript,
            assessment_type='speaking'
        )
        
        # Assertions - Basic structure
        assert 'overall_band' in result
        assert 0 <= result['overall_band'] <= 9
        assert 'band_prediction' in result
        
        # All 4 speaking criteria present
        assert 'fluency_coherence' in result
        assert 'lexical_resource' in result
        assert 'grammatical_range' in result
        assert 'pronunciation' in result
        
        # Detailed feedback components
        assert 'personalized_improvement_plan' in result
        improvement_plan = result['personalized_improvement_plan']
        assert 'focus_areas' in improvement_plan
        assert 'immediate_actions' in improvement_plan
        assert 'weekly_practice_schedule' in improvement_plan
        assert 'target_overall_band' in improvement_plan
        assert 'estimated_timeline' in improvement_plan
        
        # Verify focus areas structure
        if len(improvement_plan['focus_areas']) > 0:
            focus_area = improvement_plan['focus_areas'][0]
            assert 'criterion' in focus_area
            assert 'current_band' in focus_area
            assert 'target_band' in focus_area
            assert 'specific_weakness' in focus_area
            assert 'practice_activities' in focus_area
            assert 'estimated_time' in focus_area
        
        # Performance summary
        assert 'performance_summary' in result
        assert 'strongest_criterion' in result['performance_summary']
        assert 'weakest_criterion' in result['performance_summary']
        
        # Detailed feedback present
        assert 'detailed_feedback' in result
