"""
IELTS Listening Test Service
Handles storage, retrieval, and scoring for listening tests
Supports full-length practice tests with instant answer key validation
"""
import json
import boto3
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
from decimal import Decimal

class ListeningTestService:
    """Service for managing IELTS listening tests"""
    
    def __init__(self):
        # Initialize AWS clients
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        self.s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        self.cloudfront_domain = os.environ.get('CLOUDFRONT_DOMAIN', 'd1234567890.cloudfront.net')
        self.bucket_name = os.environ.get('AUDIO_BUCKET', 'ielts-audio-content')
        
        # Table names
        self.tests_table = self.dynamodb.Table('ielts-listening-tests')
        self.questions_table = self.dynamodb.Table('ielts-listening-questions')
        self.answers_table = self.dynamodb.Table('ielts-listening-answers')
        self.progress_table = self.dynamodb.Table('ielts-test-progress')
    
    # ============================================================================
    # TEST DATA MANAGEMENT
    # ============================================================================
    
    def create_listening_test(self, test_data: Dict) -> Dict[str, Any]:
        """
        Create a new listening test with all sections
        """
        test_id = test_data['test_id']
        
        # Store test metadata
        test_item = {
            'test_id': test_id,
            'test_type': test_data['test_type'],  # 'academic' or 'general'
            'test_number': test_data['test_number'],
            'title': test_data.get('title', f"{test_data['test_type'].title()} Listening Test {test_data['test_number']}"),
            'total_questions': 40,
            'duration_minutes': 30,
            'transfer_time_minutes': 10,
            'sections': [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Process each section
        for section in test_data['sections']:
            section_data = {
                'section_number': section['number'],
                'title': section['title'],
                'audio_filename': section['audio_filename'],
                'audio_url': None,  # Will be set when audio is uploaded
                'question_range': section['question_range'],
                'question_count': section['question_count'],
                'visual_aid': section.get('visual_aid'),
                'instructions': section.get('instructions', '')
            }
            
            # Generate pre-signed URL for audio
            if section['audio_filename']:
                audio_key = f"listening/{test_data['test_type']}/test-{test_data['test_number']}/audio/section{section['number']}.mp3"
                section_data['audio_key'] = audio_key
                section_data['audio_url'] = self.get_cloudfront_url(audio_key)
            
            # Handle visual aids (like maps)
            if section.get('visual_aid'):
                image_key = f"listening/{test_data['test_type']}/test-{test_data['test_number']}/images/{section['visual_aid']}"
                section_data['visual_aid_key'] = image_key
                section_data['visual_aid_url'] = self.get_cloudfront_url(image_key)
            
            test_item['sections'].append(section_data)
        
        # Store in DynamoDB
        self.tests_table.put_item(Item=test_item)
        
        return {
            'success': True,
            'test_id': test_id,
            'message': f"Created listening test: {test_id}"
        }
    
    def store_questions(self, test_id: str, questions: List[Dict]) -> Dict[str, Any]:
        """
        Store all questions for a listening test
        """
        stored_count = 0
        
        with self.questions_table.batch_writer() as batch:
            for q in questions:
                question_item = {
                    'question_id': f"{test_id}-q{q['number']}",
                    'test_id': test_id,
                    'section': q['section'],
                    'question_number': q['number'],
                    'question_type': q['type'],  # 'form_completion', 'multiple_choice', 'map_labeling', etc.
                    'question_text': q.get('text', ''),
                    'instructions': q.get('instructions', ''),
                    'options': q.get('options', []),  # For multiple choice
                    'max_words': q.get('max_words'),  # For completion questions
                    'created_at': datetime.utcnow().isoformat()
                }
                
                batch.put_item(Item=question_item)
                stored_count += 1
        
        return {
            'success': True,
            'questions_stored': stored_count
        }
    
    def store_answer_key(self, test_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Store answer key for a listening test (server-side only)
        """
        # Hash answers for security
        answer_hash = hashlib.sha256(json.dumps(answers, sort_keys=True).encode()).hexdigest()
        
        answer_item = {
            'test_id': test_id,
            'answer_key': answers,
            'answer_hash': answer_hash,
            'band_score_conversion': self.get_band_score_table(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.answers_table.put_item(Item=answer_item)
        
        return {
            'success': True,
            'test_id': test_id,
            'answer_count': len(answers)
        }
    
    # ============================================================================
    # TEST RETRIEVAL & DELIVERY
    # ============================================================================
    
    def get_listening_test(self, test_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get listening test for user (without answers)
        """
        # Get test metadata
        response = self.tests_table.get_item(Key={'test_id': test_id})
        if 'Item' not in response:
            return {'error': 'Test not found'}
        
        test = response['Item']
        
        # Generate temporary pre-signed URLs for audio (valid for test duration + buffer)
        for section in test['sections']:
            if section.get('audio_key'):
                section['audio_url'] = self.generate_presigned_url(
                    section['audio_key'],
                    expires_in=3600  # 1 hour
                )
            if section.get('visual_aid_key'):
                section['visual_aid_url'] = self.generate_presigned_url(
                    section['visual_aid_key'],
                    expires_in=3600
                )
        
        # Get questions
        questions = self.get_questions_for_test(test_id)
        
        # Initialize or get user progress
        progress = self.init_user_progress(test_id, user_id)
        
        return {
            'test': test,
            'questions': questions,
            'progress': progress,
            'start_time': datetime.utcnow().isoformat()
        }
    
    def get_questions_for_test(self, test_id: str) -> List[Dict]:
        """
        Get all questions for a test (without answers)
        """
        response = self.questions_table.query(
            IndexName='test-id-index',
            KeyConditionExpression='test_id = :tid',
            ExpressionAttributeValues={':tid': test_id}
        )
        
        questions = response.get('Items', [])
        
        # Sort by question number and remove answer keys
        questions.sort(key=lambda x: x['question_number'])
        
        # Clean questions for client
        for q in questions:
            q.pop('created_at', None)
            # Never send answers to client
        
        return questions
    
    # ============================================================================
    # ANSWER VALIDATION & SCORING
    # ============================================================================
    
    def validate_answers(
        self, 
        test_id: str, 
        user_answers: Dict[str, str],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Validate user answers and calculate score
        Returns detailed results without revealing correct answers during practice
        """
        # Get answer key from database
        response = self.answers_table.get_item(Key={'test_id': test_id})
        if 'Item' not in response:
            return {'error': 'Answer key not found'}
        
        answer_key = response['Item']['answer_key']
        band_conversion = response['Item']['band_score_conversion']
        
        # Compare answers
        results = {
            'correct': 0,
            'incorrect': 0,
            'unanswered': 0,
            'question_results': {},
            'section_scores': {1: 0, 2: 0, 3: 0, 4: 0}
        }
        
        for q_num in range(1, 41):  # 40 questions
            q_key = str(q_num)
            correct_answer = answer_key.get(q_key, '').strip().upper()
            user_answer = user_answers.get(q_key, '').strip().upper()
            
            # Determine section (1-10, 11-20, 21-30, 31-40)
            section = ((q_num - 1) // 10) + 1
            
            if not user_answer:
                results['unanswered'] += 1
                results['question_results'][q_key] = 'unanswered'
            elif self.compare_answers(user_answer, correct_answer):
                results['correct'] += 1
                results['section_scores'][section] += 1
                results['question_results'][q_key] = 'correct'
            else:
                results['incorrect'] += 1
                results['question_results'][q_key] = 'incorrect'
        
        # Calculate band score
        total_correct = results['correct']
        band_score = self.calculate_band_score(total_correct, band_conversion)
        
        # Store results
        self.store_test_result(test_id, user_id, results, band_score)
        
        # Return results (without revealing correct answers in practice mode)
        return {
            'test_id': test_id,
            'total_questions': 40,
            'correct': results['correct'],
            'incorrect': results['incorrect'],
            'unanswered': results['unanswered'],
            'band_score': band_score,
            'section_performance': [
                {'section': i, 'score': results['section_scores'][i], 'total': 10}
                for i in range(1, 5)
            ],
            'completed_at': datetime.utcnow().isoformat()
        }
    
    def compare_answers(self, user_answer: str, correct_answer: str) -> bool:
        """
        Compare user answer with correct answer
        Handles various answer formats
        """
        # Exact match (most common)
        if user_answer == correct_answer:
            return True
        
        # Handle number variations (e.g., "15" vs "15th" vs "fifteen")
        if self.normalize_number(user_answer) == self.normalize_number(correct_answer):
            return True
        
        # Handle alternatives separated by /
        if '/' in correct_answer:
            alternatives = [alt.strip().upper() for alt in correct_answer.split('/')]
            if user_answer in alternatives:
                return True
        
        return False
    
    def normalize_number(self, text: str) -> str:
        """
        Normalize numbers for comparison
        """
        # Remove common suffixes
        text = text.replace('ST', '').replace('ND', '').replace('RD', '').replace('TH', '')
        
        # Basic number word to digit mapping
        number_words = {
            'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4', 'FIVE': '5',
            'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9', 'TEN': '10',
            'ELEVEN': '11', 'TWELVE': '12', 'THIRTEEN': '13', 'FOURTEEN': '14',
            'FIFTEEN': '15', 'SIXTEEN': '16', 'SEVENTEEN': '17', 'EIGHTEEN': '18',
            'NINETEEN': '19', 'TWENTY': '20', 'THIRTY': '30', 'FORTY': '40',
            'FIFTY': '50', 'SIXTY': '60', 'SEVENTY': '70', 'EIGHTY': '80',
            'NINETY': '90', 'HUNDRED': '100'
        }
        
        for word, digit in number_words.items():
            text = text.replace(word, digit)
        
        return text.strip()
    
    def calculate_band_score(self, correct_count: int, band_table: Dict) -> float:
        """
        Calculate IELTS band score based on correct answers
        """
        # Default band score table for listening
        default_table = {
            '39-40': 9.0,
            '37-38': 8.5,
            '35-36': 8.0,
            '32-34': 7.5,
            '30-31': 7.0,
            '26-29': 6.5,
            '23-25': 6.0,
            '18-22': 5.5,
            '16-17': 5.0,
            '13-15': 4.5,
            '11-12': 4.0,
            '8-10': 3.5,
            '6-7': 3.0,
            '4-5': 2.5
        }
        
        band_table = band_table or default_table
        
        for range_str, band in band_table.items():
            if '-' in range_str:
                min_val, max_val = map(int, range_str.split('-'))
                if min_val <= correct_count <= max_val:
                    return float(band)
        
        # Below minimum
        return 2.0 if correct_count < 4 else 2.5
    
    # ============================================================================
    # PROGRESS TRACKING
    # ============================================================================
    
    def init_user_progress(self, test_id: str, user_id: str) -> Dict[str, Any]:
        """
        Initialize or retrieve user progress for a test
        """
        progress_id = f"{user_id}#{test_id}"
        
        # Check if progress exists
        response = self.progress_table.get_item(Key={'progress_id': progress_id})
        
        if 'Item' in response:
            return response['Item']
        
        # Create new progress
        progress = {
            'progress_id': progress_id,
            'user_id': user_id,
            'test_id': test_id,
            'current_section': 1,
            'current_question': 1,
            'answers': {},
            'time_remaining': 1800,  # 30 minutes in seconds
            'status': 'in_progress',
            'started_at': datetime.utcnow().isoformat()
        }
        
        self.progress_table.put_item(Item=progress)
        return progress
    
    def update_progress(
        self,
        test_id: str,
        user_id: str,
        current_question: int,
        answers: Dict[str, str],
        time_remaining: int
    ) -> Dict[str, Any]:
        """
        Update user progress during test
        """
        progress_id = f"{user_id}#{test_id}"
        
        # Calculate current section
        current_section = ((current_question - 1) // 10) + 1
        
        response = self.progress_table.update_item(
            Key={'progress_id': progress_id},
            UpdateExpression='SET current_section = :cs, current_question = :cq, answers = :ans, time_remaining = :tr, last_updated = :lu',
            ExpressionAttributeValues={
                ':cs': current_section,
                ':cq': current_question,
                ':ans': answers,
                ':tr': time_remaining,
                ':lu': datetime.utcnow().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        
        return response.get('Attributes', {})
    
    def store_test_result(
        self,
        test_id: str,
        user_id: str,
        results: Dict,
        band_score: float
    ) -> None:
        """
        Store final test results
        """
        result_item = {
            'result_id': f"{user_id}#{test_id}#{datetime.utcnow().isoformat()}",
            'user_id': user_id,
            'test_id': test_id,
            'test_type': 'listening',
            'correct_answers': results['correct'],
            'total_questions': 40,
            'band_score': Decimal(str(band_score)),
            'section_scores': results['section_scores'],
            'completed_at': datetime.utcnow().isoformat()
        }
        
        # Store in results table
        results_table = self.dynamodb.Table('ielts-test-results')
        results_table.put_item(Item=result_item)
    
    # ============================================================================
    # UTILITY FUNCTIONS
    # ============================================================================
    
    def get_cloudfront_url(self, key: str) -> str:
        """
        Generate CloudFront URL for a resource
        """
        return f"https://{self.cloudfront_domain}/{key}"
    
    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate pre-signed URL for S3 object
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"Error generating pre-signed URL: {e}")
            return self.get_cloudfront_url(key)
    
    def get_band_score_table(self) -> Dict[str, float]:
        """
        Get standard IELTS listening band score conversion table
        """
        return {
            '39-40': 9.0,
            '37-38': 8.5,
            '35-36': 8.0,
            '32-34': 7.5,
            '30-31': 7.0,
            '26-29': 6.5,
            '23-25': 6.0,
            '18-22': 5.5,
            '16-17': 5.0,
            '13-15': 4.5,
            '11-12': 4.0,
            '8-10': 3.5,
            '6-7': 3.0,
            '4-5': 2.5,
            '0-3': 2.0
        }