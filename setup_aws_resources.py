#!/usr/bin/env python3
"""
Setup AWS resources for IELTS Listening Tests
Creates S3 bucket and DynamoDB tables
"""
import os
import boto3
from botocore.exceptions import ClientError
import json

# AWS configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def create_s3_bucket():
    """Create S3 bucket for audio content with proper configuration"""
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    bucket_name = 'ielts-audio-content'
    
    print(f"🪣 Creating S3 bucket: {bucket_name}")
    
    try:
        # Check if bucket already exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket '{bucket_name}' already exists")
        return bucket_name
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Bucket doesn't exist, create it
            try:
                if AWS_REGION == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                    )
                
                # Set bucket policy for CloudFront access
                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                }
                
                s3_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
                
                # Enable CORS
                cors_configuration = {
                    'CORSRules': [{
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': ['GET', 'HEAD'],
                        'AllowedOrigins': ['*'],
                        'ExposeHeaders': ['Content-Length'],
                        'MaxAgeSeconds': 3600
                    }]
                }
                
                s3_client.put_bucket_cors(
                    Bucket=bucket_name,
                    CORSConfiguration=cors_configuration
                )
                
                print(f"✓ Created S3 bucket '{bucket_name}' in {AWS_REGION}")
                return bucket_name
                
            except ClientError as create_error:
                print(f"✗ Error creating bucket: {create_error}")
                return None
        else:
            print(f"✗ Error checking bucket: {e}")
            return None

def create_dynamodb_tables():
    """Create all necessary DynamoDB tables"""
    dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
    
    tables_created = []
    tables_config = [
        {
            'TableName': 'ielts-listening-tests',
            'KeySchema': [
                {'AttributeName': 'test_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'Tags': [
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'Component', 'Value': 'ListeningTests'}
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
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'ielts-listening-answers',
            'KeySchema': [
                {'AttributeName': 'test_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'ielts-test-progress',
            'KeySchema': [
                {'AttributeName': 'progress_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'progress_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'ielts-test-results',
            'KeySchema': [
                {'AttributeName': 'result_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'result_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'test_id', 'AttributeType': 'S'},
                {'AttributeName': 'completed_at', 'AttributeType': 'N'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'user-id-index',
                    'Keys': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'completed_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'test-id-index',
                    'Keys': [
                        {'AttributeName': 'test_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'ielts-reading-tests',
            'KeySchema': [
                {'AttributeName': 'test_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'ielts-reading-questions',
            'KeySchema': [
                {'AttributeName': 'question_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'question_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'ielts-reading-answers',
            'KeySchema': [
                {'AttributeName': 'test_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'ielts-full-tests',
            'KeySchema': [
                {'AttributeName': 'full_test_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'full_test_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    print(f"\n📊 Creating DynamoDB tables in {AWS_REGION}...")
    
    for table_config in tables_config:
        table_name = table_config['TableName']
        
        try:
            # Check if table already exists
            existing_tables = dynamodb.list_tables()['TableNames']
            
            if table_name in existing_tables:
                print(f"✓ Table '{table_name}' already exists")
                tables_created.append(table_name)
            else:
                # Create the table
                params = {
                    'TableName': table_name,
                    'KeySchema': table_config['KeySchema'],
                    'AttributeDefinitions': table_config['AttributeDefinitions'],
                    'BillingMode': table_config['BillingMode']
                }
                
                # Add GSI if present
                if 'GlobalSecondaryIndexes' in table_config:
                    # Fix GSI structure
                    gsi_list = []
                    for gsi in table_config['GlobalSecondaryIndexes']:
                        gsi_item = {
                            'IndexName': gsi['IndexName'],
                            'KeySchema': gsi['Keys'],
                            'Projection': gsi['Projection']
                        }
                        gsi_list.append(gsi_item)
                    params['GlobalSecondaryIndexes'] = gsi_list
                
                # Add tags if present
                if 'Tags' in table_config:
                    params['Tags'] = table_config['Tags']
                
                dynamodb.create_table(**params)
                print(f"✓ Created table '{table_name}'")
                tables_created.append(table_name)
                
        except ClientError as e:
            if 'ResourceInUseException' in str(e):
                print(f"✓ Table '{table_name}' already exists")
                tables_created.append(table_name)
            else:
                print(f"✗ Error creating table '{table_name}': {e}")
    
    return tables_created

def verify_existing_tables():
    """Verify and list all existing IELTS-related DynamoDB tables"""
    dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
    
    try:
        all_tables = dynamodb.list_tables()['TableNames']
        ielts_tables = [t for t in all_tables if 'ielts' in t.lower()]
        
        if ielts_tables:
            print("\n📋 Existing IELTS DynamoDB tables:")
            for table in sorted(ielts_tables):
                # Get table description for more info
                try:
                    desc = dynamodb.describe_table(TableName=table)
                    item_count = desc['Table'].get('ItemCount', 0)
                    status = desc['Table']['TableStatus']
                    print(f"  • {table} (Status: {status}, Items: {item_count})")
                except:
                    print(f"  • {table}")
        
        return ielts_tables
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []

def main():
    """Main function to set up all AWS resources"""
    print("=" * 60)
    print("🚀 SETTING UP AWS RESOURCES FOR IELTS LISTENING TESTS")
    print("=" * 60)
    print(f"Region: {AWS_REGION}")
    print()
    
    # Create S3 bucket
    bucket = create_s3_bucket()
    
    # Create DynamoDB tables
    tables = create_dynamodb_tables()
    
    # Verify existing tables
    existing = verify_existing_tables()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ AWS RESOURCES SETUP COMPLETE")
    print("=" * 60)
    
    if bucket:
        print(f"\n📦 S3 Bucket:")
        print(f"  • Name: {bucket}")
        print(f"  • Region: {AWS_REGION}")
        print(f"  • URL: https://{bucket}.s3.{AWS_REGION}.amazonaws.com/")
    
    if tables:
        print(f"\n📊 DynamoDB Tables Created/Verified: {len(tables)}")
        for table in tables:
            print(f"  • {table}")
    
    print("\n🎯 Next Steps:")
    print("  1. Upload audio files and images to S3")
    print("  2. Load test data into DynamoDB")
    print("  3. Configure CloudFront distribution (optional)")
    
    return {
        'success': True,
        's3_bucket': bucket,
        'dynamodb_tables': tables,
        'existing_tables': existing
    }

if __name__ == "__main__":
    result = main()
    print(f"\n📄 Setup Result:")
    print(json.dumps(result, indent=2))