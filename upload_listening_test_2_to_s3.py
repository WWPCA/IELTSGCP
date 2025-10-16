#!/usr/bin/env python3
"""
Upload Academic Listening Test 2 audio files to S3
"""
import boto3
import os
from datetime import datetime
from parse_listening_test_2_data import ListeningTest2Parser

def upload_listening_test_2():
    """Upload Test 2 audio files to S3 and store in DynamoDB"""
    
    # Initialize AWS services
    s3 = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    # S3 bucket name
    bucket_name = 'ielts-audio-content'
    
    # DynamoDB tables
    tests_table = dynamodb.Table('ielts-listening-tests')
    questions_table = dynamodb.Table('ielts-listening-questions')
    answers_table = dynamodb.Table('ielts-listening-answers')
    
    # Parse test data
    parser = ListeningTest2Parser()
    parsed_data = parser.parse_academic_test_2()
    
    test_id = 'academic-listening-test-2'
    test_data = parsed_data['test_data']
    
    print(f"📝 Processing Academic Listening Test 2...")
    
    # Audio files to upload (from attached_assets folder)
    audio_files = [
        {
            'local': 'attached_assets/Academic_Listening_Test_2_Section_1_1760643350030.mp3',
            's3_key': f'listening-tests/{test_id}/section-1.mp3',
            'section': 1
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_2_Section_2_1760643350028.mp3',
            's3_key': f'listening-tests/{test_id}/section-2.mp3',
            'section': 2
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_2_Section_3_1760643350030.mp3',
            's3_key': f'listening-tests/{test_id}/section-3.mp3',
            'section': 3
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_2_Section_4_1760643350030.mp3',
            's3_key': f'listening-tests/{test_id}/section-4.mp3',
            'section': 4
        }
    ]
    
    # Upload audio files
    audio_urls = {}
    for file_info in audio_files:
        try:
            # Check if file exists
            if os.path.exists(file_info['local']):
                # Upload to S3
                with open(file_info['local'], 'rb') as audio_file:
                    s3.put_object(
                        Bucket=bucket_name,
                        Key=file_info['s3_key'],
                        Body=audio_file,
                        ContentType='audio/mpeg',
                        Metadata={
                            'test_id': test_id,
                            'section': str(file_info['section']),
                            'test_type': 'academic'
                        }
                    )
                
                # Store S3 key for database
                audio_urls[f"section_{file_info['section']}"] = file_info['s3_key']
                print(f"✓ Uploaded Section {file_info['section']} audio")
            else:
                print(f"⚠️ File not found: {file_info['local']}")
                
        except Exception as e:
            print(f"Error uploading {file_info['local']}: {e}")
    
    # Store test metadata in DynamoDB
    test_item = {
        'test_id': test_id,
        'test_type': 'academic',
        'test_number': 2,
        'title': 'IELTS Academic Listening Test 2',
        'total_questions': 40,
        'duration_minutes': 30,
        'sections': [
            {
                'section_number': 1,
                'title': 'Library Registration',
                'description': 'Conversation between a student and a librarian',
                'question_range': '1-10',
                'audio_s3_key': audio_urls.get('section_1', ''),
                'duration_seconds': 300
            },
            {
                'section_number': 2,
                'title': 'National Science Museum Tour',
                'description': 'Tour guide describing the museum',
                'question_range': '11-20',
                'audio_s3_key': audio_urls.get('section_2', ''),
                'duration_seconds': 360
            },
            {
                'section_number': 3,
                'title': 'Psychology Research Project',
                'description': 'Two students discussing their research',
                'question_range': '21-30',
                'audio_s3_key': audio_urls.get('section_3', ''),
                'duration_seconds': 360
            },
            {
                'section_number': 4,
                'title': 'Water Conservation Strategies',
                'description': 'Lecture about urban water conservation',
                'question_range': '31-40',
                'audio_s3_key': audio_urls.get('section_4', ''),
                'duration_seconds': 420
            }
        ],
        'created_at': datetime.utcnow().isoformat()
    }
    
    tests_table.put_item(Item=test_item)
    print("✓ Test metadata stored")
    
    # Store questions
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
            'context': q.get('context', ''),
            'created_at': datetime.utcnow().isoformat()
        }
        
        questions_table.put_item(Item=question_item)
        questions_stored += 1
    
    print(f"✓ {questions_stored} questions stored")
    
    # Store answer key
    from decimal import Decimal
    
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
        'answer_variations': parsed_data.get('answer_variations', {}),
        'band_score_conversion': band_score_conversion,
        'created_at': datetime.utcnow().isoformat()
    }
    
    answers_table.put_item(Item=answer_item)
    print("✓ Answer key stored")
    
    print(f"\n✅ Academic Listening Test 2 successfully uploaded!")
    print(f"   Test ID: {test_id}")
    print(f"   Audio files: {len(audio_urls)} sections uploaded to S3")
    print(f"   Questions: {questions_stored}")
    print(f"   Bucket: {bucket_name}")
    
    return {
        'success': True,
        'test_id': test_id,
        'audio_files': len(audio_urls),
        'questions_loaded': questions_stored
    }

if __name__ == "__main__":
    result = upload_listening_test_2()