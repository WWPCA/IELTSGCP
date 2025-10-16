"""
IELTS Reading Test Service
Handles reading test data management and instant scoring
"""
import boto3
from boto3.dynamodb.types import Decimal
from datetime import datetime, timedelta
import hashlib
import json
from typing import Dict, List, Any, Optional
import os

class ReadingTestService:
    """Service for managing IELTS reading tests"""
    
    def __init__(self):
        """Initialize service with DynamoDB connection"""
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        
        # DynamoDB tables
        self.tests_table = self.dynamodb.Table('ielts-reading-tests')
        self.questions_table = self.dynamodb.Table('ielts-reading-questions')
        self.answers_table = self.dynamodb.Table('ielts-reading-answers')
        
        # Other shared tables
        self.progress_table = self.dynamodb.Table('ielts-test-progress')
        self.results_table = self.dynamodb.Table('ielts-test-results')
    
    # ============================================================================
    # TEST CREATION & SETUP
    # ============================================================================
    
    def create_reading_test(self, test_data: Dict) -> Dict[str, Any]:
        """
        Create a new reading test with all passages
        """
        test_id = test_data['test_id']
        
        # Store test metadata
        test_item = {
            'test_id': test_id,
            'test_type': test_data['test_type'],  # 'academic' or 'general'
            'test_number': test_data['test_number'],
            'title': test_data.get('title', f"{test_data['test_type'].title()} Reading Test {test_data['test_number']}"),
            'total_questions': 40,
            'duration_minutes': 60,
            'passages': [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Process each passage
        for passage in test_data['passages']:
            passage_data = {
                'passage_number': passage['number'],
                'title': passage['title'],
                'word_count': passage.get('word_count', 900),
                'question_range': passage['question_range'],
                'question_count': passage['question_count'],
                'time_recommended': passage.get('time_recommended', 20)
            }
            test_item['passages'].append(passage_data)
        
        # Store in DynamoDB
        self.tests_table.put_item(Item=test_item)
        
        return {
            'success': True,
            'test_id': test_id,
            'message': f"Created reading test: {test_id}"
        }
    
    def store_questions(self, test_id: str, questions: List[Dict]) -> Dict[str, Any]:
        """
        Store all questions for a reading test
        """
        stored_count = 0
        
        with self.questions_table.batch_writer() as batch:
            for q in questions:
                question_item = {
                    'question_id': f"{test_id}-q{q['number']}",
                    'test_id': test_id,
                    'passage': q['passage'],
                    'question_number': q['number'],
                    'question_type': q['type'],
                    'question_text': q.get('text', ''),
                    'instructions': q.get('instructions', ''),
                    'options': q.get('options', []),
                    'max_words': q.get('max_words'),
                    'option_descriptions': q.get('option_descriptions', {}),
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
        Store answer key for a reading test (server-side only)
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
    
    def get_reading_test(self, test_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get reading test for user (without answers)
        """
        # Get test metadata
        response = self.tests_table.get_item(Key={'test_id': test_id})
        if 'Item' not in response:
            return {'error': 'Test not found'}
        
        test = response['Item']
        
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
            'passage_scores': {1: 0, 2: 0, 3: 0}
        }
        
        for i in range(1, 41):
            question_num = str(i)
            correct_answer = answer_key.get(question_num, '').upper()
            user_answer = user_answers.get(question_num, '').upper().strip()
            
            if not user_answer:
                results['unanswered'] += 1
                results['question_results'][question_num] = 'unanswered'
            elif self.check_answer(user_answer, correct_answer):
                results['correct'] += 1
                results['question_results'][question_num] = 'correct'
                
                # Track passage performance
                if i <= 13:
                    results['passage_scores'][1] += 1
                elif i <= 26:
                    results['passage_scores'][2] += 1
                else:
                    results['passage_scores'][3] += 1
            else:
                results['incorrect'] += 1
                results['question_results'][question_num] = 'incorrect'
        
        # Calculate band score
        band_score = self.calculate_band_score(results['correct'], band_conversion)
        
        # Store result
        self.store_test_result(
            test_id=test_id,
            user_id=user_id,
            results=results,
            band_score=band_score
        )
        
        # Format passage performance
        passage_performance = []
        passage_questions = {1: 13, 2: 13, 3: 14}  # Q per passage
        
        for passage_num in [1, 2, 3]:
            passage_performance.append({
                'passage': passage_num,
                'score': results['passage_scores'][passage_num],
                'total': passage_questions[passage_num],
                'percentage': round(
                    (results['passage_scores'][passage_num] / passage_questions[passage_num]) * 100, 1
                )
            })
        
        return {
            'correct': results['correct'],
            'incorrect': results['incorrect'],
            'unanswered': results['unanswered'],
            'total_questions': 40,
            'band_score': band_score,
            'passage_performance': passage_performance,
            'completed_at': datetime.utcnow().isoformat()
        }
    
    def check_answer(self, user_answer: str, correct_answer: str) -> bool:
        """
        Check if user answer matches correct answer
        Handles different answer formats
        """
        # Clean answers
        user_answer = user_answer.strip().upper()
        correct_answer = correct_answer.strip().upper()
        
        # Direct match
        if user_answer == correct_answer:
            return True
        
        # Handle text answers (remove extra spaces, punctuation)
        import re
        user_clean = re.sub(r'[^\w\s]', '', user_answer.lower()).strip()
        correct_clean = re.sub(r'[^\w\s]', '', correct_answer.lower()).strip()
        
        # Allow minor variations (e.g., plural/singular)
        if user_clean == correct_clean:
            return True
        
        # Check if key words match for text answers
        if len(correct_clean.split()) > 1:
            # For multi-word answers, check if all key words present
            correct_words = set(correct_clean.split())
            user_words = set(user_clean.split())
            
            # If user has all the key words (allowing some flexibility)
            if correct_words.issubset(user_words) or user_words.issubset(correct_words):
                return True
        
        return False
    
    def calculate_band_score(self, correct_answers: int, band_table: Dict) -> float:
        """
        Calculate IELTS band score based on correct answers
        """
        # Convert string keys to use with Decimal values
        for range_str, score in band_table.items():
            if '-' in range_str:
                min_val, max_val = map(int, range_str.split('-'))
                if min_val <= correct_answers <= max_val:
                    return float(score) if isinstance(score, Decimal) else score
        
        # Default to lowest score
        return 2.0
    
    # ============================================================================
    # PROGRESS MANAGEMENT
    # ============================================================================
    
    def init_user_progress(self, test_id: str, user_id: str) -> Dict:
        """
        Initialize or retrieve user's test progress
        """
        progress_id = f"{user_id}#{test_id}"
        
        try:
            response = self.progress_table.get_item(Key={'progress_id': progress_id})
            
            if 'Item' in response:
                return response['Item']
            else:
                # Create new progress entry
                progress = {
                    'progress_id': progress_id,
                    'user_id': user_id,
                    'test_id': test_id,
                    'test_type': 'reading',
                    'current_passage': 1,
                    'current_question': 1,
                    'answers': {},
                    'time_remaining': 3600,  # 60 minutes in seconds
                    'status': 'in_progress',
                    'started_at': datetime.utcnow().isoformat()
                }
                
                self.progress_table.put_item(Item=progress)
                return progress
                
        except Exception as e:
            print(f"Error managing progress: {e}")
            return {
                'current_question': 1,
                'answers': {},
                'time_remaining': 3600
            }
    
    def update_progress(
        self,
        test_id: str,
        user_id: str,
        current_question: int,
        answers: Dict[str, str],
        time_remaining: int
    ) -> Dict:
        """
        Update user's test progress
        """
        progress_id = f"{user_id}#{test_id}"
        
        # Determine current passage based on question number
        if current_question <= 13:
            current_passage = 1
        elif current_question <= 26:
            current_passage = 2
        else:
            current_passage = 3
        
        try:
            self.progress_table.update_item(
                Key={'progress_id': progress_id},
                UpdateExpression='SET current_question = :q, current_passage = :p, answers = :a, time_remaining = :t, last_updated = :u',
                ExpressionAttributeValues={
                    ':q': current_question,
                    ':p': current_passage,
                    ':a': answers,
                    ':t': time_remaining,
                    ':u': datetime.utcnow().isoformat()
                }
            )
            
            return {
                'success': True,
                'current_question': current_question,
                'current_passage': current_passage
            }
            
        except Exception as e:
            print(f"Error updating progress: {e}")
            return {'success': False, 'error': str(e)}
    
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
            'test_type': 'reading',
            'correct_answers': results['correct'],
            'total_questions': 40,
            'band_score': Decimal(str(band_score)),
            'passage_scores': results['passage_scores'],
            'completed_at': datetime.utcnow().isoformat()
        }
        
        # Store in results table
        self.results_table.put_item(Item=result_item)
    
    # ============================================================================
    # UTILITY FUNCTIONS
    # ============================================================================
    
    def get_band_score_table(self) -> Dict[str, float]:
        """
        Get standard IELTS reading band score conversion table for Academic
        """
        return {
            '39-40': Decimal('9.0'),
            '37-38': Decimal('8.5'),
            '35-36': Decimal('8.0'),
            '33-34': Decimal('7.5'),
            '30-32': Decimal('7.0'),
            '27-29': Decimal('6.5'),
            '23-26': Decimal('6.0'),
            '19-22': Decimal('5.5'),
            '15-18': Decimal('5.0'),
            '13-14': Decimal('4.5'),
            '10-12': Decimal('4.0'),
            '8-9': Decimal('3.5'),
            '6-7': Decimal('3.0'),
            '4-5': Decimal('2.5'),
            '0-3': Decimal('2.0')
        }