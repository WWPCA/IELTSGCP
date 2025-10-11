"""
Gemini 2.5 Flash Service for Text-based Assessments
Replaces AWS Bedrock Nova Micro with Google Gemini 2.5 Flash
"""
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from google import genai
    from google.genai import types
except ImportError:
    # Fallback for testing environments where google-genai might not be available
    genai = None
    types = None

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for Gemini 2.5 Flash text-based AI processing"""
    
    def __init__(self, project_id: Optional[str] = None, region: str = 'us-central1'):
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.region = region
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set either as parameter or environment variable")
        
        if not genai:
            raise ImportError("google-genai package is not installed or not available")
        
        # Configure for Vertex AI
        os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
        os.environ['GOOGLE_CLOUD_LOCATION'] = self.region
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
        
        # Initialize client
        try:
            self.client = genai.Client()
            self.model_id = 'gemini-2.5-flash'
            logger.info(f"Gemini service initialized - project: {self.project_id}, region: {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
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
        """Generate comprehensive evaluation prompt for writing tasks with detailed IELTS rubrics"""
        
        word_requirement = 150 if 'task1' in task_type else 250
        first_criterion = "Task Achievement" if 'task1' in task_type else "Task Response"
        
        prompt = f"""You are an expert IELTS examiner with deep knowledge of official IELTS writing band descriptors. Evaluate this {task_type.replace('_', ' ').title()} response with precision and detail.

OFFICIAL IELTS WRITING BAND DESCRIPTORS:

{first_criterion}:
Band 9: Fully addresses all parts. Clear position. Fully extended, well-supported ideas.
Band 7-8: Addresses all parts. Clear position. Relevant, extended, well-supported ideas.
Band 5-6: Addresses task but format/coverage may be incomplete. Position unclear. Limited support/development.
Band 3-4: Does not address all parts. Unclear position. Limited/irrelevant ideas.

Coherence and Cohesion:
Band 9: Skillful paragraphing. Cohesion that never attracts attention.
Band 7-8: Logical organization. Clear progression. Skillful use of cohesive devices.
Band 5-6: Some organization/progression. Inadequate/inaccurate/overuse of cohesive devices.
Band 3-4: Information/ideas not arranged coherently. Very limited linking.

Lexical Resource:
Band 9: Wide range. Natural, sophisticated control. Rare minor errors.
Band 7-8: Sufficient flexibility. Less common lexical items with awareness of style. Occasional errors.
Band 5-6: Adequate range. Attempts less common vocabulary with errors. Noticeable spelling errors.
Band 3-4: Very limited range. Errors may severely distort meaning.

Grammatical Range and Accuracy:
Band 9: Wide range. Full flexibility. Error-free.
Band 7-8: Variety of complex structures. Frequent error-free sentences. Good control.
Band 5-6: Mix of simple/complex. Frequent errors but meaning clear.
Band 3-4: Very limited range. Errors predominate. May severely distort meaning.

TASK PROMPT:
{task_prompt}

STUDENT RESPONSE (Word count: {word_count}/{word_requirement} required):
{student_response}

EVALUATION INSTRUCTIONS:
1. Carefully assess against all 4 IELTS criteria using official band descriptors
2. Quote specific examples from the student's response
3. Provide precise band scores (use .5 increments: 6.0, 6.5, 7.0, etc.)
4. Give detailed, actionable feedback with specific improvement strategies

Provide evaluation in the following JSON format:

{{
    "overall_band": <float 0-9 (average of 4 criteria)>,
    "band_prediction": "<e.g., 'Band 7.0 - Good User'>",
    "{first_criterion.lower().replace(' ', '_')}": {{
        "score": <float 0-9>,
        "band_descriptor": "<which band level achieved and why>",
        "strengths": [
            "<specific strength with quote>",
            "<another strength with evidence>"
        ],
        "weaknesses": [
            "<specific weakness with example>",
            "<area needing development>"
        ],
        "specific_examples": {{
            "positive": ["<quote showing task addressed well>"],
            "negative": ["<quote showing task not fully addressed>"]
        }},
        "commentary": "<detailed paragraph analyzing task response>"
    }},
    "coherence_cohesion": {{
        "score": <float 0-9>,
        "band_descriptor": "<band level and justification>",
        "strengths": [
            "<organizational strength with example>",
            "<cohesive device used well>"
        ],
        "weaknesses": [
            "<organizational issue with example>",
            "<cohesion problem>"
        ],
        "specific_examples": {{
            "positive": ["<effective paragraph structure/linking>"],
            "negative": ["<poor cohesion/organization>"]
        }},
        "paragraphing": "<assessment of paragraph structure>",
        "cohesive_devices": "<analysis of linking words/phrases>",
        "commentary": "<detailed analysis>"
    }},
    "lexical_resource": {{
        "score": <float 0-9>,
        "band_descriptor": "<band level and why>",
        "strengths": [
            "<effective vocabulary with examples>",
            "<range/precision shown>"
        ],
        "weaknesses": [
            "<vocabulary errors with corrections>",
            "<limited range in specific areas>"
        ],
        "specific_examples": {{
            "positive": ["<sophisticated/appropriate vocabulary used>"],
            "negative": ["<errors: 'incorrect word' → 'correction'>"]
        }},
        "vocabulary_range": "<assessment of range and flexibility>",
        "spelling_accuracy": "<spelling assessment>",
        "commentary": "<detailed analysis>"
    }},
    "grammatical_range_accuracy": {{
        "score": <float 0-9>,
        "band_descriptor": "<band level and justification>",
        "strengths": [
            "<complex structures used successfully>",
            "<accuracy in specific areas>"
        ],
        "weaknesses": [
            "<grammatical errors with corrections>",
            "<limited structure variety>"
        ],
        "specific_examples": {{
            "positive": ["<correct complex sentences>"],
            "negative": ["<error: 'incorrect' → 'correction'>"]
        }},
        "structure_variety": "<assessment of range>",
        "error_frequency": "<how often errors occur>",
        "commentary": "<detailed analysis>"
    }},
    "word_count_assessment": {{
        "meets_requirement": <boolean>,
        "actual_count": {word_count},
        "required_minimum": {word_requirement},
        "impact": "<penalty description if under minimum>"
    }},
    "detailed_feedback": "<comprehensive 2-3 paragraph analysis covering: overall performance, how well task was addressed, organization quality, vocabulary and grammar highlights, and main areas for improvement>",
    "performance_summary": {{
        "strongest_criterion": "<which criterion scored highest>",
        "weakest_criterion": "<which needs most work>",
        "key_takeaway": "<main insight about writing level>"
    }},
    "sample_improvements": [
        "{{\"original\": \"<sentence from response>\", \"improved\": \"<better version>\", \"reason\": \"<why this is better>\"}}",
        "{{\"original\": \"<another sentence>\", \"improved\": \"<improved version>\", \"reason\": \"<explanation>\"}}"
    ],
    "recommendations": [
        "{{\"priority\": \"high\", \"area\": \"<criterion>\", \"action\": \"<specific improvement step>\", \"example\": \"<how to practice>\"}}",
        "{{\"priority\": \"high\", \"area\": \"<criterion>\", \"action\": \"<another key action>\", \"example\": \"<practice method>\"}}",
        "{{\"priority\": \"medium\", \"area\": \"<criterion>\", \"action\": \"<development area>\", \"example\": \"<how to improve>\"}}"
    ],
    "personalized_improvement_plan": {{
        "focus_areas": [
            "{{\"criterion\": \"<weakest criterion>\", \"current_band\": <score>, \"target_band\": <score + 0.5 or 1.0>, \"specific_issues\": [\"<issue 1>\", \"<issue 2>\"], \"practice_activities\": [\"<activity 1>\", \"<activity 2>\", \"<activity 3>\"], \"estimated_time\": \"<e.g., 3-4 weeks with consistent practice>\"}}",
            "{{\"criterion\": \"<second weakest>\", \"current_band\": <score>, \"target_band\": <score + 0.5>, \"specific_issues\": [\"<issue>\"], \"practice_activities\": [\"<activity 1>\", \"<activity 2>\"], \"estimated_time\": \"<timeframe>\"}}"
        ],
        "immediate_actions": [
            "<action you can take today to improve>",
            "<another quick improvement step>",
            "<one more immediate practice activity>"
        ],
        "study_schedule": {{
            "daily_practice": "<15-30 min focused practice on weakest area>",
            "weekly_focus": "<dedicate 2-3 hours to targeted exercises>",
            "monthly_milestone": "<complete X practice tasks, review all feedback>"
        }},
        "writing_exercises": [
            "<specific type of writing practice based on weaknesses>",
            "<targeted grammar/vocabulary exercises>",
            "<timed writing practice recommendations>"
        ],
        "target_overall_band": <current_band + 0.5 or 1.0>,
        "estimated_timeline": "<realistic timeframe to achieve target, e.g., 6-8 weeks with regular practice>",
        "progress_tracking": {{
            "track_these_metrics": [\"<metric 1 based on weakness>\", \"<metric 2>\"],
            "reassess_after": "<timeframe for next practice test>"
        }}
    }},
    "next_steps": [
        "<specific study recommendation>",
        "<practice activity>",
        "<resource or technique>"
    ]
}}

IMPORTANT:
- Quote specific sentences/phrases from the response as evidence
- Provide corrections for errors (show original → improved)
- Be precise with band scores using official descriptors
- Give constructive, actionable feedback with clear examples
- Create a personalized improvement plan that's realistic and achievable
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
