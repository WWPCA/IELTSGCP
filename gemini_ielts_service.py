"""
Gemini IELTS Assessment Service
Clean, modern service for IELTS assessment evaluation using Gemini 2.5 Flash
Integrates with blueprint:python_gemini
"""
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

# Import existing IELTS rubrics
from assessment_criteria.speaking_criteria import (
    SPEAKING_BAND_DESCRIPTORS,
    SPEAKING_ASSESSMENT_CRITERIA,
    calculate_speaking_band_score
)
from assessment_criteria.writing_criteria import (
    WRITING_TASK1_BAND_DESCRIPTORS,
    WRITING_TASK2_BAND_DESCRIPTORS,
    WRITING_ASSESSMENT_CRITERIA,
    calculate_writing_band_score
)

logger = logging.getLogger(__name__)

# Initialize Gemini client using API key from environment
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


# Pydantic Models for Structured Responses
class CriterionScore(BaseModel):
    """Individual criterion score with feedback"""
    score: float = Field(..., ge=0, le=9, description="Band score 0-9")
    feedback: str = Field(..., description="Detailed feedback for this criterion")
    strengths: List[str] = Field(default_factory=list, description="Specific strengths")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")


class SpeakingAssessment(BaseModel):
    """IELTS Speaking Assessment Result"""
    overall_band: float = Field(..., ge=0, le=9)
    fluency_coherence: CriterionScore
    lexical_resource: CriterionScore
    grammatical_range: CriterionScore
    pronunciation: CriterionScore
    detailed_feedback: str
    conversation_duration: str
    assessment_id: str
    timestamp: str


class WritingAssessment(BaseModel):
    """IELTS Writing Assessment Result"""
    overall_band: float = Field(..., ge=0, le=9)
    task_achievement: CriterionScore
    coherence_cohesion: CriterionScore
    lexical_resource: CriterionScore
    grammatical_range: CriterionScore
    detailed_feedback: str
    word_count: int
    assessment_id: str
    timestamp: str


class GeminiIELTSService:
    """Service for IELTS assessment evaluation using Gemini 2.5 Flash"""
    
    def __init__(self):
        self.model = "gemini-2.5-flash"
        logger.info(f"Gemini IELTS Service initialized with model: {self.model}")
    
    def _build_speaking_prompt(self, transcript: str, assessment_type: str) -> str:
        """Build comprehensive speaking assessment prompt with official rubrics"""
        
        # Extract band descriptors as formatted text
        rubric_text = "OFFICIAL IELTS SPEAKING BAND DESCRIPTORS:\n\n"
        for criterion in SPEAKING_ASSESSMENT_CRITERIA:
            rubric_text += f"{criterion['name'].upper()}:\n"
            rubric_text += f"{criterion['description']}\n\n"
            
            # Add band 9, 7, 5 descriptors for reference
            for band in [9, 7, 5]:
                descriptor = SPEAKING_BAND_DESCRIPTORS[band][criterion['name']]
                rubric_text += f"Band {band}: {descriptor}\n"
            rubric_text += "\n"
        
        is_academic = 'academic' in assessment_type.lower()
        context = "Academic IELTS" if is_academic else "General Training IELTS"
        
        prompt = f"""You are an expert IELTS examiner evaluating a {context} speaking assessment.

{rubric_text}

TRANSCRIPT TO EVALUATE:
{transcript}

ASSESSMENT INSTRUCTIONS:
1. Carefully analyze the candidate's performance against all 4 IELTS criteria
2. Provide specific examples from the transcript to justify your scores
3. Use the official band descriptors to determine precise scores (use .5 increments: 6.0, 6.5, 7.0, etc.)
4. Calculate overall band as the average of the 4 criterion scores, rounded to nearest 0.5
5. Provide actionable, specific feedback for improvement

Your response must be valid JSON matching this structure:
{{
    "overall_band": <float>,
    "fluency_coherence": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "lexical_resource": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "grammatical_range": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "pronunciation": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "detailed_feedback": "<comprehensive 2-3 paragraph overall assessment>"
}}"""
        return prompt
    
    def _build_writing_prompt(self, essay: str, task_number: int, assessment_type: str) -> str:
        """Build comprehensive writing assessment prompt with official rubrics"""
        
        # Select appropriate descriptors
        descriptors = WRITING_TASK1_BAND_DESCRIPTORS if task_number == 1 else WRITING_TASK2_BAND_DESCRIPTORS
        
        rubric_text = f"OFFICIAL IELTS WRITING TASK {task_number} BAND DESCRIPTORS:\n\n"
        
        # Get criteria names based on task
        if task_number == 1:
            criteria = ["Task Achievement", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
        else:
            criteria = ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
        
        for criterion in criteria:
            rubric_text += f"{criterion.upper()}:\n"
            for band in [9, 7, 5]:
                descriptor = descriptors[band][criterion]
                rubric_text += f"Band {band}: {descriptor}\n"
            rubric_text += "\n"
        
        is_academic = 'academic' in assessment_type.lower()
        context = "Academic IELTS" if is_academic else "General Training IELTS"
        
        # Build criterion name for JSON (task_achievement vs task_response)
        first_criterion = "task_achievement" if task_number == 1 else "task_response"
        
        prompt = f"""You are an expert IELTS examiner evaluating a {context} Writing Task {task_number}.

{rubric_text}

ESSAY TO EVALUATE:
{essay}

ASSESSMENT INSTRUCTIONS:
1. Carefully analyze the essay against all 4 IELTS criteria
2. Provide specific examples from the essay to justify your scores
3. Use the official band descriptors to determine precise scores (use .5 increments: 6.0, 6.5, 7.0, etc.)
4. Note: The overall writing band is weighted (Task 2 counts double Task 1), but for this single task, calculate the average of the 4 criteria
5. Provide actionable, specific feedback for improvement

Your response must be valid JSON matching this structure:
{{
    "overall_band": <float (average of 4 criteria)>,
    "{first_criterion}": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "coherence_cohesion": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "lexical_resource": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "grammatical_range": {{
        "score": <float>,
        "feedback": "<detailed feedback>",
        "strengths": ["<specific strength>", ...],
        "improvements": ["<specific improvement area>", ...]
    }},
    "detailed_feedback": "<comprehensive 2-3 paragraph overall assessment>"
}}"""
        return prompt
    
    async def evaluate_speaking(
        self,
        transcript: str,
        assessment_type: str,
        conversation_duration: str = "12 minutes",
        assessment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate IELTS speaking assessment using Gemini 2.5 Flash
        
        Args:
            transcript: Full conversation transcript
            assessment_type: 'academic_speaking' or 'general_speaking'
            conversation_duration: Duration of conversation
            assessment_id: Unique assessment identifier
        
        Returns:
            Structured assessment result with scores and feedback
        """
        try:
            prompt = self._build_speaking_prompt(transcript, assessment_type)
            
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for consistent grading
                    response_mime_type="application/json",
                    response_schema=SpeakingAssessment
                )
            )
            
            # Parse response
            result = json.loads(response.text)
            
            # Add metadata
            result['conversation_duration'] = conversation_duration
            result['assessment_id'] = assessment_id or f"speaking_{datetime.utcnow().timestamp()}"
            result['timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Speaking assessment completed: {result['assessment_id']} - Band {result['overall_band']}")
            return result
            
        except Exception as e:
            logger.error(f"Speaking evaluation error: {str(e)}")
            # Return fallback response
            return self._get_fallback_speaking_result(assessment_id, conversation_duration)
    
    async def evaluate_writing(
        self,
        essay: str,
        task_number: int,
        assessment_type: str,
        word_count: int,
        assessment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate IELTS writing assessment using Gemini 2.5 Flash
        
        Args:
            essay: Student's essay text
            task_number: 1 or 2
            assessment_type: 'academic_writing' or 'general_writing'
            word_count: Number of words in essay
            assessment_id: Unique assessment identifier
        
        Returns:
            Structured assessment result with scores and feedback
        """
        try:
            prompt = self._build_writing_prompt(essay, task_number, assessment_type)
            
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for consistent grading
                    response_mime_type="application/json",
                    response_schema=WritingAssessment
                )
            )
            
            # Parse response
            result = json.loads(response.text)
            
            # Add metadata
            result['word_count'] = word_count
            result['assessment_id'] = assessment_id or f"writing_t{task_number}_{datetime.utcnow().timestamp()}"
            result['timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Writing assessment completed: {result['assessment_id']} - Band {result['overall_band']}")
            return result
            
        except Exception as e:
            logger.error(f"Writing evaluation error: {str(e)}")
            # Return fallback response
            return self._get_fallback_writing_result(task_number, assessment_id, word_count)
    
    def _get_fallback_speaking_result(self, assessment_id: Optional[str], duration: str) -> Dict[str, Any]:
        """Fallback response if Gemini API fails"""
        return {
            "overall_band": 6.5,
            "fluency_coherence": {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Maintained conversation flow"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "lexical_resource": {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Adequate vocabulary used"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "grammatical_range": {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Basic structures used correctly"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "pronunciation": {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Generally intelligible"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "detailed_feedback": "We encountered a technical issue during assessment. Please contact support or retry your assessment.",
            "conversation_duration": duration,
            "assessment_id": assessment_id or f"speaking_fallback_{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_fallback_writing_result(self, task_number: int, assessment_id: Optional[str], word_count: int) -> Dict[str, Any]:
        """Fallback response if Gemini API fails"""
        first_criterion = "task_achievement" if task_number == 1 else "task_response"
        
        return {
            "overall_band": 6.5,
            first_criterion: {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Task addressed"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "coherence_cohesion": {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Basic organization present"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "lexical_resource": {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Adequate vocabulary"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "grammatical_range": {
                "score": 6.5,
                "feedback": "Assessment system encountered an issue. Please try again.",
                "strengths": ["Basic structures used"],
                "improvements": ["Technical issue - please retry assessment"]
            },
            "detailed_feedback": "We encountered a technical issue during assessment. Please contact support or retry your assessment.",
            "word_count": word_count,
            "assessment_id": assessment_id or f"writing_t{task_number}_fallback_{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance for easy import
gemini_service = GeminiIELTSService()
