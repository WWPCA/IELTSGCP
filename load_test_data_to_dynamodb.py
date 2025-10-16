#!/usr/bin/env python3
"""
Load Academic Listening Test 1 data into DynamoDB
"""
import boto3
from datetime import datetime
from parse_listening_test_data import ListeningTestParser
from decimal import Decimal
import os

def load_test_to_dynamodb():
    """Load test data into DynamoDB tables"""
    
    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    # Get tables
    tests_table = dynamodb.Table('ielts-listening-tests')
    questions_table = dynamodb.Table('ielts-listening-questions')
    answers_table = dynamodb.Table('ielts-listening-answers')
    
    # Parse test data
    parser = ListeningTestParser()
    parsed_data = parser.parse_academic_test_1()
    
    test_id = 'academic-listening-test-1'
    
    print(f"📝 Loading test data for: {test_id}")
    
    # 1. Store test metadata
    test_item = {
        'test_id': test_id,
        'test_type': 'academic',
        'test_number': 1,
        'title': 'IELTS Academic Listening Test 1',
        'total_questions': 40,
        'duration_minutes': 30,
        'transfer_time_minutes': 10,
        'sections': [
            {
                'section_number': 1,
                'title': 'Student Accommodation Request',
                'audio_key': 'listening/academic/test-1/audio/section1.mp3',
                'question_range': '1-10',
                'question_count': 10,
                'description': 'Conversation between a student and a housing officer'
            },
            {
                'section_number': 2,
                'title': 'Bellingham Castle Tour',
                'audio_key': 'listening/academic/test-1/audio/section2.mp3',
                'visual_aid_key': 'listening/academic/test-1/images/section2_castle_map.png',
                'question_range': '11-20',
                'question_count': 10,
                'description': 'Tour guide giving information about a historic castle'
            },
            {
                'section_number': 3,
                'title': 'Renewable Energy Research Project',
                'audio_key': 'listening/academic/test-1/audio/section3.mp3',
                'question_range': '21-30',
                'question_count': 10,
                'description': 'Two students discussing their research project'
            },
            {
                'section_number': 4,
                'title': 'Social Media and Mental Health',
                'audio_key': 'listening/academic/test-1/audio/section4.mp3',
                'question_range': '31-40',
                'question_count': 10,
                'description': 'Lecture about the impact of social media on mental health'
            }
        ],
        'created_at': datetime.utcnow().isoformat()
    }
    
    tests_table.put_item(Item=test_item)
    print("✓ Test metadata stored")
    
    # 2. Store questions
    questions_stored = 0
    for q in parsed_data['questions']:
        question_item = {
            'question_id': f"{test_id}-q{q['number']}",
            'test_id': test_id,
            'section': q['section'],
            'question_number': q['number'],
            'question_type': q['type'],
            'question_text': q.get('text', ''),
            'instructions': q.get('instructions', ''),
            'options': q.get('options', []),
            'max_words': q.get('max_words'),
            'requires_visual': q.get('requires_visual', False),
            'option_descriptions': q.get('option_descriptions', {}),
            'created_at': datetime.utcnow().isoformat()
        }
        
        questions_table.put_item(Item=question_item)
        questions_stored += 1
    
    print(f"✓ {questions_stored} questions stored")
    
    # 3. Store answer key (server-side only)
    answer_item = {
        'test_id': test_id,
        'answer_key': parsed_data['answers'],
        'band_score_conversion': {
            '39-40': Decimal('9.0'),
            '37-38': Decimal('8.5'),
            '35-36': Decimal('8.0'),
            '32-34': Decimal('7.5'),
            '30-31': Decimal('7.0'),
            '26-29': Decimal('6.5'),
            '23-25': Decimal('6.0'),
            '18-22': Decimal('5.5'),
            '16-17': Decimal('5.0'),
            '13-15': Decimal('4.5'),
            '11-12': Decimal('4.0'),
            '8-10': Decimal('3.5'),
            '6-7': Decimal('3.0'),
            '4-5': Decimal('2.5'),
            '0-3': Decimal('2.0')
        },
        'created_at': datetime.utcnow().isoformat()
    }
    
    answers_table.put_item(Item=answer_item)
    print("✓ Answer key stored")
    
    print("\n✅ Academic Listening Test 1 successfully loaded to DynamoDB!")
    print(f"   Test ID: {test_id}")
    print(f"   Questions: {questions_stored}")
    print(f"   Sections: 4")
    print(f"   Duration: 30 minutes + 10 minutes transfer time")
    
    return {
        'success': True,
        'test_id': test_id,
        'questions_loaded': questions_stored
    }

if __name__ == "__main__":
    result = load_test_to_dynamodb()
    print(f"\nResult: {result}")