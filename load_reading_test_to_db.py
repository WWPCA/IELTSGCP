#!/usr/bin/env python3
"""
Load Academic Reading Test 1 data into DynamoDB
"""
import boto3
from datetime import datetime
from parse_reading_test_data import ReadingTestParser
from decimal import Decimal
import os

def load_reading_test_to_dynamodb():
    """Load reading test data into DynamoDB tables"""
    
    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    # Get tables
    tests_table = dynamodb.Table('ielts-reading-tests')
    questions_table = dynamodb.Table('ielts-reading-questions')
    answers_table = dynamodb.Table('ielts-reading-answers')
    
    # Parse test data
    parser = ReadingTestParser()
    parsed_data = parser.parse_academic_test_1()
    
    test_id = 'academic-reading-test-1'
    
    print(f"📝 Loading reading test data for: {test_id}")
    
    # 1. Store test metadata
    test_item = {
        'test_id': test_id,
        'test_type': 'academic',
        'test_number': 1,
        'title': 'IELTS Academic Reading Test 1',
        'total_questions': 40,
        'duration_minutes': 60,
        'passages': [
            {
                'passage_number': 1,
                'title': 'The History of Urban Vertical Farming',
                'word_count': 850,
                'question_range': '1-13',
                'question_count': 13,
                'time_recommended': 20
            },
            {
                'passage_number': 2,
                'title': 'The Cognitive Benefits of Bilingualism',
                'word_count': 900,
                'question_range': '14-26',
                'question_count': 13,
                'time_recommended': 20
            },
            {
                'passage_number': 3,
                'title': 'The Economics of Happiness',
                'word_count': 950,
                'question_range': '27-40',
                'question_count': 14,
                'time_recommended': 20
            }
        ],
        'created_at': datetime.utcnow().isoformat()
    }
    
    tests_table.put_item(Item=test_item)
    print("✓ Test metadata stored")
    
    # 2. Store questions
    questions_stored = 0
    for q in parsed_data['questions']:
        # Handle option_descriptions if present
        question_item = {
            'question_id': f"{test_id}-q{q['number']}",
            'test_id': test_id,
            'passage': q['passage'],
            'question_number': q['number'],
            'question_type': q['type'],
            'question_text': q.get('text', ''),
            'instructions': q.get('instructions', ''),
            'options': q.get('options', []),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Add optional fields if present
        if q.get('max_words'):
            question_item['max_words'] = q['max_words']
        
        if q.get('option_descriptions'):
            question_item['option_descriptions'] = q['option_descriptions']
        
        questions_table.put_item(Item=question_item)
        questions_stored += 1
    
    print(f"✓ {questions_stored} questions stored")
    
    # 3. Store answer key (server-side only)
    # Convert band scores to Decimal for DynamoDB
    band_score_conversion = {
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
    
    answer_item = {
        'test_id': test_id,
        'answer_key': parsed_data['answers'],
        'band_score_conversion': band_score_conversion,
        'created_at': datetime.utcnow().isoformat()
    }
    
    answers_table.put_item(Item=answer_item)
    print("✓ Answer key stored")
    
    print("\n✅ Academic Reading Test 1 successfully loaded to DynamoDB!")
    print(f"   Test ID: {test_id}")
    print(f"   Questions: {questions_stored}")
    print(f"   Passages: 3")
    print(f"   Duration: 60 minutes")
    print("\n📊 Question Types:")
    print("   • Paragraph matching (Q1-6)")
    print("   • Multiple choice (Q7-10, Q36-40)")
    print("   • Sentence completion (Q11-13)")
    print("   • True/False/Not Given (Q14-18)")
    print("   • Matching groups (Q19-22)")
    print("   • Summary completion (Q23-26)")
    print("   • Heading matching (Q27-30)")
    print("   • Yes/No/Not Given (Q31-35)")
    
    return {
        'success': True,
        'test_id': test_id,
        'questions_loaded': questions_stored
    }

if __name__ == "__main__":
    result = load_reading_test_to_dynamodb()
    print(f"\nResult: {result}")