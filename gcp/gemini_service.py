"""
Gemini 2.5 Flash Service for Text-based Assessments
Replaces AWS Bedrock Nova Micro with Google Gemini 2.5 Flash
"""
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for Gemini 2.5 Flash text-based AI processing"""
    
    def __init__(self, project_id: Optional[str] = None, region: str = 'us-central1'):
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.region = region
        
        # Configure for Vertex AI
        os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
        os.environ['GOOGLE_CLOUD_LOCATION'] = self.region
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
        
        # Initialize client
        self.client = genai.Client()
        self.model_id = 'gemini-2.5-flash'
        
        logger.info(f"Gemini service initialized - project: {self.project_id}, region: {self.region}")
    
    async def evaluate_writing_task(
        self,
        task_type: str,
        task_prompt: str,
        student_response: str,
        word_count: int
    ) -> Dict[str, Any]:
        """
        Evaluate IELTS writing task using Gemini 2.5 Flash
        
        Args:
            task_type: 'academic_task1', 'academic_task2', 'general_task1', 'general_task2'
            task_prompt: The writing task prompt
            student_response: Student's written response
            word_count: Number of words in response
        
        Returns:
            Structured evaluation with band scores and feedback
        """
        evaluation_prompt = self._get_writing_evaluation_prompt(
            task_type, task_prompt, student_response, word_count
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=evaluation_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.3,  # Lower temperature for consistent evaluations
                    max_output_tokens=2048
                )
            )
            
            evaluation = json.loads(response.text)
            
            # Add metadata
            evaluation['evaluated_at'] = datetime.utcnow().isoformat()
            evaluation['word_count'] = word_count
            evaluation['task_type'] = task_type
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Failed to evaluate writing task: {e}")
            raise
    
    def _get_writing_evaluation_prompt(
        self,
        task_type: str,
        task_prompt: str,
        student_response: str,
        word_count: int
    ) -> str:
        """Generate evaluation prompt for writing tasks"""
        
        criteria = {
            'academic_task1': ['Task Achievement', 'Coherence and Cohesion', 'Lexical Resource', 'Grammatical Range and Accuracy'],
            'academic_task2': ['Task Response', 'Coherence and Cohesion', 'Lexical Resource', 'Grammatical Range and Accuracy'],
            'general_task1': ['Task Achievement', 'Coherence and Cohesion', 'Lexical Resource', 'Grammatical Range and Accuracy'],
            'general_task2': ['Task Response', 'Coherence and Cohesion', 'Lexical Resource', 'Grammatical Range and Accuracy']
        }
        
        word_requirement = 150 if 'task1' in task_type else 250
        
        prompt = f"""You are an experienced IELTS examiner evaluating a {task_type.replace('_', ' ').title()} response.

TASK PROMPT:
{task_prompt}

STUDENT RESPONSE (Word count: {word_count}):
{student_response}

Evaluate this response according to official IELTS writing assessment criteria and provide feedback in the following JSON format:

{{
    "overall_band": <float 0-9>,
    "task_achievement": {{
        "score": <float 0-9>,
        "strengths": [<list of specific strengths>],
        "weaknesses": [<list of specific areas for improvement>],
        "commentary": "<detailed analysis>"
    }},
    "coherence_cohesion": {{
        "score": <float 0-9>,
        "strengths": [<list>],
        "weaknesses": [<list>],
        "commentary": "<analysis>"
    }},
    "lexical_resource": {{
        "score": <float 0-9>,
        "strengths": [<list>],
        "weaknesses": [<list>],
        "commentary": "<analysis>"
    }},
    "grammatical_range": {{
        "score": <float 0-9>,
        "strengths": [<list>],
        "weaknesses": [<list>],
        "commentary": "<analysis>"
    }},
    "detailed_feedback": "<comprehensive paragraph with specific examples from the response>",
    "word_count_assessment": "{{'meets_requirement': <boolean>, 'note': '<comment if under {word_requirement} words>'}}",
    "recommendations": [<list of 3-5 actionable recommendations for improvement>]
}}

Important:
- Be specific and reference actual examples from the student's response
- Scores should be realistic and aligned with IELTS band descriptors
- Overall band is the average of the four criteria scores
- Provide constructive, encouraging feedback
"""
        return prompt
    
    async def generate_speaking_questions(
        self,
        part: int,
        previous_topic: Optional[str] = None
    ) -> List[str]:
        """
        Generate IELTS speaking questions for different parts
        
        Args:
            part: Speaking test part (1, 2, or 3)
            previous_topic: Topic from Part 2 (required for Part 3)
        
        Returns:
            List of questions
        """
        if part == 1:
            prompt = """Generate 8-10 IELTS Speaking Part 1 questions covering 2-3 familiar topics (e.g., home, work, hobbies, food).

Return as JSON array: ["question1", "question2", ...]
"""
        elif part == 2:
            prompt = """Generate an IELTS Speaking Part 2 topic card.

Return as JSON:
{
    "topic": "<topic title>",
    "description": "<You should say: bullet points>",
    "questions": ["<guiding questions>"]
}
"""
        else:  # Part 3
            if not previous_topic:
                previous_topic = "technology"
            
            prompt = f"""Generate 6-8 IELTS Speaking Part 3 questions related to the topic: {previous_topic}

These should be more abstract and require critical thinking.

Return as JSON array: ["question1", "question2", ...]
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.7
                )
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Failed to generate speaking questions: {e}")
            raise
    
    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Check content for safety and appropriateness
        
        Returns:
            {
                'is_safe': bool,
                'severity': 'none' | 'mild' | 'moderate' | 'severe',
                'categories': List[str]
            }
        """
        prompt = f"""Analyze the following text for inappropriate content in an IELTS assessment context.

Text: {text}

Check for:
- Profanity
- Hate speech
- Sexual content
- Violence
- Off-topic (completely unrelated to IELTS/English learning)

Return JSON:
{{
    "is_safe": <boolean>,
    "severity": "<none|mild|moderate|severe>",
    "categories": [<list of triggered categories>],
    "explanation": "<brief explanation>"
}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.1
                )
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Content moderation error: {e}")
            # Fail safe
            return {
                'is_safe': True,
                'severity': 'none',
                'categories': [],
                'explanation': 'Moderation service unavailable'
            }
    
    async def generate_personalized_study_plan(
        self,
        user_assessments: List[Dict[str, Any]],
        target_band: float
    ) -> Dict[str, Any]:
        """
        Generate personalized IELTS study plan based on assessment history
        
        Args:
            user_assessments: List of completed assessments with scores
            target_band: Target IELTS band score
        
        Returns:
            Personalized study plan with recommendations
        """
        assessment_summary = json.dumps(user_assessments, indent=2)
        
        prompt = f"""Based on the following IELTS assessment history, create a personalized study plan.

Assessment History:
{assessment_summary}

Target Band Score: {target_band}

Generate a comprehensive study plan in JSON format:
{{
    "current_level": {{
        "overall_band": <float>,
        "strongest_skills": [<list>],
        "weakest_skills": [<list>]
    }},
    "gap_analysis": {{
        "points_to_target": <float>,
        "estimated_study_time": "<time estimate>",
        "priority_areas": [<ordered list>]
    }},
    "weekly_study_plan": {{
        "speaking": {{
            "hours_per_week": <int>,
            "activities": [<list of specific activities>]
        }},
        "writing": {{
            "hours_per_week": <int>,
            "activities": [<list>]
        }},
        "reading": {{
            "hours_per_week": <int>,
            "activities": [<list>]
        }},
        "listening": {{
            "hours_per_week": <int>,
            "activities": [<list>]
        }}
    }},
    "specific_recommendations": [<list of 5-7 actionable recommendations>],
    "milestone_goals": [<list of 3-4 milestone goals with timelines>]
}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.5,
                    max_output_tokens=2048
                )
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Failed to generate study plan: {e}")
            raise
