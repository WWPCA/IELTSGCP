#!/usr/bin/env python3
"""
Script to store Academic Listening Test 1 data
Processes audio files, questions, and answers into DynamoDB
"""
import os
import json
import boto3
import shutil
from parse_listening_test_data import ListeningTestParser
from listening_test_service import ListeningTestService
from pathlib import Path

def upload_files_to_s3():
    """
    Upload audio files and images to S3
    """
    s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    bucket_name = os.environ.get('AUDIO_BUCKET', 'ielts-audio-content')
    
    # Define file mappings
    files_to_upload = [
        {
            'local': 'attached_assets/IELTS_Academic_Listening_Test_1_Section_1_Student_Accomodation_Request_1760630519084.mp3',
            's3_key': 'listening/academic/test-1/audio/section1.mp3',
            'section': 1
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_2_Bellingham_Castle_Tour_1760630519083.mp3',
            's3_key': 'listening/academic/test-1/audio/section2.mp3',
            'section': 2
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_3_Renewable_Energy_Research_Project_1760630519083.mp3',
            's3_key': 'listening/academic/test-1/audio/section3.mp3',
            'section': 3
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_4_Lecture_1760630519082.mp3',
            's3_key': 'listening/academic/test-1/audio/section4.mp3',
            'section': 4
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_2_Map_1760630519083.png',
            's3_key': 'listening/academic/test-1/images/section2_castle_map.png',
            'type': 'image'
        }
    ]
    
    uploaded_files = {}
    
    for file_info in files_to_upload:
        local_path = file_info['local']
        s3_key = file_info['s3_key']
        
        if os.path.exists(local_path):
            try:
                # Determine content type
                if local_path.endswith('.mp3'):
                    content_type = 'audio/mpeg'
                elif local_path.endswith('.png'):
                    content_type = 'image/png'
                else:
                    content_type = 'application/octet-stream'
                
                # Upload to S3
                print(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}")
                
                with open(local_path, 'rb') as file:
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=s3_key,
                        Body=file,
                        ContentType=content_type,
                        CacheControl='max-age=31536000',  # Cache for 1 year
                        Metadata={
                            'test': 'academic-listening-test-1',
                            'section': str(file_info.get('section', '')),
                            'type': file_info.get('type', 'audio')
                        }
                    )
                
                uploaded_files[s3_key] = True
                print(f"✓ Uploaded: {s3_key}")
                
            except Exception as e:
                print(f"✗ Failed to upload {local_path}: {e}")
                uploaded_files[s3_key] = False
        else:
            print(f"✗ File not found: {local_path}")
            uploaded_files[s3_key] = False
    
    return uploaded_files

def create_dynamodb_tables():
    """
    Create DynamoDB tables if they don't exist
    """
    dynamodb = boto3.client('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    tables_to_create = [
        {
            'TableName': 'ielts-listening-tests',
            'KeySchema': [
                {'AttributeName': 'test_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ]
        },
        {
            'TableName': 'ielts-listening-questions',
            'KeySchema': [
                {'AttributeName': 'question_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'question_id', 'AttributeType': 'S'},
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'test-id-index',
                    'Keys': [
                        {'AttributeName': 'test_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ]
        },
        {
            'TableName': 'ielts-listening-answers',
            'KeySchema': [
                {'AttributeName': 'test_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ]
        },
        {
            'TableName': 'ielts-test-progress',
            'KeySchema': [
                {'AttributeName': 'progress_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'progress_id', 'AttributeType': 'S'}
            ]
        },
        {
            'TableName': 'ielts-test-results',
            'KeySchema': [
                {'AttributeName': 'result_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'result_id', 'AttributeType': 'S'}
            ]
        }
    ]
    
    for table_config in tables_to_create:
        try:
            # Check if table exists
            existing_tables = dynamodb.list_tables()['TableNames']
            if table_config['TableName'] in existing_tables:
                print(f"✓ Table {table_config['TableName']} already exists")
                continue
            
            # Create table
            params = {
                'TableName': table_config['TableName'],
                'KeySchema': table_config['KeySchema'],
                'AttributeDefinitions': table_config['AttributeDefinitions'],
                'BillingMode': 'PAY_PER_REQUEST'
            }
            
            if 'GlobalSecondaryIndexes' in table_config:
                params['GlobalSecondaryIndexes'] = table_config['GlobalSecondaryIndexes']
            
            dynamodb.create_table(**params)
            print(f"✓ Created table: {table_config['TableName']}")
            
        except Exception as e:
            if 'ResourceInUseException' in str(e):
                print(f"✓ Table {table_config['TableName']} already exists")
            else:
                print(f"✗ Error creating table {table_config['TableName']}: {e}")

def store_test_data():
    """
    Store the test data in DynamoDB
    """
    # Parse the test data
    parser = ListeningTestParser()
    parsed_data = parser.parse_academic_test_1()
    
    # Initialize service
    service = ListeningTestService()
    
    # Store test metadata
    print("\n📝 Storing test metadata...")
    result = service.create_listening_test(parsed_data['test_data'])
    print(f"✓ {result['message']}")
    
    # Store questions
    print("\n📝 Storing questions...")
    result = service.store_questions(
        parsed_data['test_data']['test_id'],
        parsed_data['questions']
    )
    print(f"✓ Stored {result['questions_stored']} questions")
    
    # Store answer key
    print("\n🔑 Storing answer key...")
    result = service.store_answer_key(
        parsed_data['test_data']['test_id'],
        parsed_data['answers']
    )
    print(f"✓ Stored answer key with {result['answer_count']} answers")
    
    return parsed_data

def main():
    """
    Main function to store Academic Listening Test 1
    """
    print("=" * 60)
    print("STORING ACADEMIC LISTENING TEST 1")
    print("=" * 60)
    
    # Step 1: Create DynamoDB tables
    print("\n🗄️  Setting up DynamoDB tables...")
    create_dynamodb_tables()
    
    # Step 2: Upload files to S3
    print("\n☁️  Uploading files to S3...")
    uploaded = upload_files_to_s3()
    
    # Step 3: Store test data in DynamoDB
    print("\n💾 Storing test data in DynamoDB...")
    test_data = store_test_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ACADEMIC LISTENING TEST 1 STORED SUCCESSFULLY")
    print("=" * 60)
    print(f"Test ID: academic-listening-test-1")
    print(f"Questions: 40")
    print(f"Sections: 4")
    print(f"Audio files uploaded: {sum(1 for v in uploaded.values() if v)}")
    print("\nThe test is now ready for use in the full-length practice tests!")
    
    # Return test info for integration
    return {
        'test_id': 'academic-listening-test-1',
        'status': 'ready',
        'components': {
            'audio_files': uploaded,
            'questions': len(test_data['questions']),
            'answers': len(test_data['answers'])
        }
    }

if __name__ == "__main__":
    # Check if running in production environment
    if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
        result = main()
        print(json.dumps(result, indent=2))
    else:
        print("⚠️  AWS credentials not configured")
        print("This script would store the following:")
        print("- 4 audio files (MP3) to S3")
        print("- 1 map image (PNG) to S3")
        print("- 40 questions to DynamoDB")
        print("- Answer key to DynamoDB")
        print("\nTo run in production, ensure AWS credentials are set.")