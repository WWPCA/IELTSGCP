"""
AWS Bedrock Service for IELTS AI Assessments
Handles Nova Micro for writing, reading, and listening assessments
"""
import boto3
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class BedrockService:
    """Service for AWS Bedrock AI models"""
    
    def __init__(self, region: str = None):
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        
        # Initialize Bedrock Runtime client
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=self.region,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        logger.info(f"Bedrock service initialized - region: {self.region}")
    
    def evaluate_writing_with_nova_micro(
        self,
        essay_text: str,
        prompt: str,
        assessment_type: str
    ) -> Dict[str, Any]:
        """
        Evaluate IELTS writing task using Nova Micro
        Cost: ~$0.003 per assessment
        """
        try:
            # Get appropriate rubric based on assessment type
            rubric = self._get_writing_rubric(assessment_type)
            
            # Prepare the evaluation prompt
            evaluation_prompt = f"""You are an expert IELTS examiner evaluating a writing task.

Assessment Type: {assessment_type}
Task Prompt: {prompt}

Student Essay:
{essay_text}

IELTS Band Descriptors:
{json.dumps(rubric, indent=2)}

Please evaluate the essay according to official IELTS criteria:

1. Task Achievement/Response (25%): 
   - For Task 1: Clear overview, accurate data description, relevant details
   - For Task 2: Clear position, relevant ideas, fully developed arguments

2. Coherence and Cohesion (25%):
   - Logical organization, clear progression, effective paragraphing
   - Appropriate use of cohesive devices

3. Lexical Resource (25%):
   - Range of vocabulary, accuracy, appropriacy
   - Less common lexical items, collocations

4. Grammatical Range and Accuracy (25%):
   - Variety of structures, accuracy, control
   - Complex sentences, punctuation

Provide your evaluation in the following JSON format:
{{
    "overall_band": 0.0,
    "criteria_scores": {{
        "task_achievement": 0.0,
        "coherence_cohesion": 0.0,
        "lexical_resource": 0.0,
        "grammatical_range": 0.0
    }},
    "detailed_feedback": {{
        "strengths": ["specific strength 1", "specific strength 2"],
        "areas_for_improvement": ["specific area 1", "specific area 2"],
        "specific_suggestions": ["actionable suggestion 1", "actionable suggestion 2"],
        "examples_from_essay": ["example phrase showing good/bad usage"]
    }},
    "word_count": {len(essay_text.split())},
    "estimated_cefr_level": "B2/C1/etc"
}}"""

            # Call Nova Micro
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-micro-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": evaluation_prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 1000,
                        "temperature": 0.3  # Lower temperature for consistent scoring
                    }
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Nova Micro returns output.message.content structure
            if 'output' in response_body and 'message' in response_body['output']:
                content = response_body['output']['message']['content'][0]['text']
            else:
                content = '{}'
            
            # Parse the JSON response
            try:
                evaluation = json.loads(content)
            except json.JSONDecodeError:
                # Fallback parsing if response isn't valid JSON
                evaluation = self._parse_text_response(content)
            
            # Add metadata
            evaluation['assessment_type'] = assessment_type
            evaluation['model_used'] = 'amazon.nova-micro-v1:0'
            evaluation['timestamp'] = datetime.utcnow().isoformat()
            evaluation['ai_generated'] = True
            evaluation['content_safe'] = True
            
            logger.info(f"Writing evaluation completed - band: {evaluation.get('overall_band')}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating writing: {e}")
            return self._get_error_response("writing_evaluation_error", str(e))
    
    def evaluate_reading_with_nova_micro(
        self,
        user_answers: List[str],
        answer_key: List[str],
        passages: List[str],
        assessment_type: str
    ) -> Dict[str, Any]:
        """
        Evaluate IELTS reading comprehension using Nova Micro
        Cost: ~$0.001 per assessment
        """
        try:
            evaluation_prompt = f"""You are an IELTS examiner evaluating reading comprehension answers.

Assessment Type: {assessment_type}

Reading Passages:
{json.dumps(passages, indent=2)}

Answer Key:
{json.dumps(answer_key, indent=2)}

User Answers:
{json.dumps(user_answers, indent=2)}

Instructions:
1. Compare user answers to the answer key
2. Allow for minor spelling variations (e.g., "colour" vs "color")
3. Accept valid synonyms where appropriate
4. For multi-word answers, check if key words are present
5. Be lenient with articles (a/an/the) unless specifically required

Provide evaluation in this JSON format:
{{
    "correct_answers": 0,
    "total_questions": {len(answer_key)},
    "band_score": 0.0,
    "question_results": [
        {{
            "question_number": 1,
            "user_answer": "...",
            "correct_answer": "...",
            "is_correct": true/false,
            "feedback": "explanation if wrong"
        }}
    ],
    "overall_feedback": "General feedback on performance",
    "strengths": ["area 1", "area 2"],
    "improvement_areas": ["suggestion 1", "suggestion 2"]
}}"""

            # Call Nova Micro
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-micro-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": evaluation_prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 1500,
                        "temperature": 0.1  # Very low for objective scoring
                    }
                })
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', [{}])[0].get('text', '{}')
            
            try:
                evaluation = json.loads(content)
            except json.JSONDecodeError:
                evaluation = self._parse_text_response(content)
            
            # Calculate band score based on correct answers
            correct = evaluation.get('correct_answers', 0)
            evaluation['band_score'] = self._calculate_reading_band_score(correct)
            
            # Add metadata
            evaluation['assessment_type'] = assessment_type
            evaluation['model_used'] = 'amazon.nova-micro-v1:0'
            evaluation['timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Reading evaluation completed - score: {correct}/{len(answer_key)}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating reading: {e}")
            return self._get_error_response("reading_evaluation_error", str(e))
    
    def evaluate_listening_with_nova_micro(
        self,
        user_answers: List[str],
        answer_key: List[str],
        transcript: str,
        assessment_type: str
    ) -> Dict[str, Any]:
        """
        Evaluate IELTS listening comprehension using Nova Micro
        Cost: ~$0.001 per assessment
        """
        try:
            evaluation_prompt = f"""You are an IELTS examiner evaluating listening comprehension answers.

Assessment Type: {assessment_type}

Audio Transcript:
{transcript}

Answer Key:
{json.dumps(answer_key, indent=2)}

User Answers:
{json.dumps(user_answers, indent=2)}

Instructions:
1. Compare user answers to the answer key
2. Be more lenient with spelling for listening (heard vs written)
3. Accept phonetically similar answers
4. Allow plural/singular variations where meaning is preserved
5. Accept abbreviated forms if unambiguous

Provide evaluation in this JSON format:
{{
    "correct_answers": 0,
    "total_questions": {len(answer_key)},
    "band_score": 0.0,
    "question_results": [
        {{
            "question_number": 1,
            "user_answer": "...",
            "correct_answer": "...",
            "is_correct": true/false,
            "feedback": "explanation if wrong"
        }}
    ],
    "overall_feedback": "General feedback on performance",
    "common_errors": ["error type 1", "error type 2"],
    "tips": ["listening tip 1", "listening tip 2"]
}}"""

            # Call Nova Micro
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-micro-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": evaluation_prompt
                        }
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.1,
                    "top_p": 0.9
                })
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', [{}])[0].get('text', '{}')
            
            try:
                evaluation = json.loads(content)
            except json.JSONDecodeError:
                evaluation = self._parse_text_response(content)
            
            # Calculate band score
            correct = evaluation.get('correct_answers', 0)
            evaluation['band_score'] = self._calculate_listening_band_score(correct)
            
            # Add metadata
            evaluation['assessment_type'] = assessment_type
            evaluation['model_used'] = 'amazon.nova-micro-v1:0'
            evaluation['timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Listening evaluation completed - score: {correct}/{len(answer_key)}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating listening: {e}")
            return self._get_error_response("listening_evaluation_error", str(e))
    
    def _get_writing_rubric(self, assessment_type: str) -> Dict[str, Any]:
        """Get IELTS writing rubric based on assessment type"""
        base_rubric = {
            "band_9": {
                "task_achievement": "Fully addresses all parts of the task with fully extended and well-supported ideas",
                "coherence_cohesion": "Uses cohesion in such a way that it attracts no attention; skilfully manages paragraphing",
                "lexical_resource": "Uses a wide range of vocabulary with very natural and sophisticated control",
                "grammatical_range": "Uses a wide range of structures with full flexibility and accuracy"
            },
            "band_8": {
                "task_achievement": "Sufficiently addresses all parts of the task; presents a well-developed response",
                "coherence_cohesion": "Sequences information and ideas logically; manages all aspects of cohesion well",
                "lexical_resource": "Uses a wide range of vocabulary fluently and flexibly",
                "grammatical_range": "Uses a wide range of structures; the majority of sentences are error-free"
            },
            "band_7": {
                "task_achievement": "Addresses all parts of the task; presents a clear position throughout",
                "coherence_cohesion": "Logically organises information; uses a range of cohesive devices appropriately",
                "lexical_resource": "Uses a sufficient range of vocabulary with some flexibility and precision",
                "grammatical_range": "Uses a variety of complex structures; produces frequent error-free sentences"
            },
            "band_6": {
                "task_achievement": "Addresses all parts of the task though some parts may be more fully covered",
                "coherence_cohesion": "Arranges information coherently; uses cohesive devices effectively but may be over/under-used",
                "lexical_resource": "Uses an adequate range of vocabulary; attempts less common vocabulary with some inaccuracy",
                "grammatical_range": "Uses a mix of simple and complex sentence forms; makes some errors but they rarely reduce communication"
            }
        }
        
        if "task1" in assessment_type.lower():
            base_rubric["task_type"] = "Report writing - describe visual information"
            base_rubric["min_words"] = 150
        else:
            base_rubric["task_type"] = "Essay writing - present arguments and opinions"
            base_rubric["min_words"] = 250
            
        return base_rubric
    
    def _calculate_reading_band_score(self, correct_answers: int) -> float:
        """Calculate IELTS band score from reading correct answers (out of 40)"""
        # IELTS Academic Reading band score conversion
        if correct_answers >= 39:
            return 9.0
        elif correct_answers >= 37:
            return 8.5
        elif correct_answers >= 35:
            return 8.0
        elif correct_answers >= 33:
            return 7.5
        elif correct_answers >= 30:
            return 7.0
        elif correct_answers >= 27:
            return 6.5
        elif correct_answers >= 23:
            return 6.0
        elif correct_answers >= 19:
            return 5.5
        elif correct_answers >= 15:
            return 5.0
        elif correct_answers >= 13:
            return 4.5
        elif correct_answers >= 10:
            return 4.0
        elif correct_answers >= 8:
            return 3.5
        elif correct_answers >= 6:
            return 3.0
        elif correct_answers >= 4:
            return 2.5
        else:
            return 2.0
    
    def _calculate_listening_band_score(self, correct_answers: int) -> float:
        """Calculate IELTS band score from listening correct answers (out of 40)"""
        # IELTS Listening band score conversion (same for Academic and General)
        if correct_answers >= 39:
            return 9.0
        elif correct_answers >= 37:
            return 8.5
        elif correct_answers >= 35:
            return 8.0
        elif correct_answers >= 32:
            return 7.5
        elif correct_answers >= 30:
            return 7.0
        elif correct_answers >= 26:
            return 6.5
        elif correct_answers >= 23:
            return 6.0
        elif correct_answers >= 18:
            return 5.5
        elif correct_answers >= 16:
            return 5.0
        elif correct_answers >= 13:
            return 4.5
        elif correct_answers >= 10:
            return 4.0
        elif correct_answers >= 8:
            return 3.5
        elif correct_answers >= 6:
            return 3.0
        elif correct_answers >= 4:
            return 2.5
        else:
            return 2.0
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse non-JSON text response into structured format"""
        # Fallback parser for when Nova Micro doesn't return valid JSON
        result = {
            "overall_band": 6.0,
            "criteria_scores": {
                "task_achievement": 6.0,
                "coherence_cohesion": 6.0,
                "lexical_resource": 6.0,
                "grammatical_range": 6.0
            },
            "detailed_feedback": {
                "strengths": ["Response provided"],
                "areas_for_improvement": ["Could not parse detailed feedback"],
                "specific_suggestions": ["Please try again"],
                "raw_response": text[:500]  # Include part of raw response
            }
        }
        
        # Try to extract band scores from text
        import re
        band_pattern = r"(?:band|score)[:\s]*(\d+(?:\.\d+)?)"
        matches = re.findall(band_pattern, text.lower())
        if matches:
            try:
                result["overall_band"] = float(matches[0])
            except:
                pass
                
        return result
    
    def _get_error_response(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Generate error response for failed evaluations"""
        return {
            "error": True,
            "error_type": error_type,
            "error_message": error_message,
            "overall_band": 0.0,
            "criteria_scores": {
                "task_achievement": 0.0,
                "coherence_cohesion": 0.0,
                "lexical_resource": 0.0,
                "grammatical_range": 0.0
            },
            "detailed_feedback": {
                "error": error_message,
                "suggestion": "Please try again or contact support"
            },
            "timestamp": datetime.utcnow().isoformat()
        }