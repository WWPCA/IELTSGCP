#!/usr/bin/env python3
"""
Create S3 bucket and upload IELTS listening test files
Works with block public access enabled
"""
import os
import boto3
from botocore.exceptions import ClientError
import mimetypes

# AWS configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def create_s3_bucket_private():
    """Create S3 bucket with private access (no public policy)"""
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
                
                # Enable CORS for web access (doesn't require public access)
                cors_configuration = {
                    'CORSRules': [{
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': ['GET', 'HEAD'],
                        'AllowedOrigins': ['*'],
                        'ExposeHeaders': ['Content-Length', 'Content-Type'],
                        'MaxAgeSeconds': 3600
                    }]
                }
                
                s3_client.put_bucket_cors(
                    Bucket=bucket_name,
                    CORSConfiguration=cors_configuration
                )
                
                print(f"✓ Created private S3 bucket '{bucket_name}' in {AWS_REGION}")
                print("  Note: Using private bucket with pre-signed URLs for secure access")
                return bucket_name
                
            except ClientError as create_error:
                print(f"✗ Error creating bucket: {create_error}")
                return None
        else:
            print(f"✗ Error checking bucket: {e}")
            return None

def upload_listening_test_files(bucket_name):
    """Upload Academic Listening Test 1 files to S3"""
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    # Define files to upload
    files_to_upload = [
        {
            'local': 'attached_assets/IELTS_Academic_Listening_Test_1_Section_1_Student_Accomodation_Request_1760630519084.mp3',
            's3_key': 'listening/academic/test-1/audio/section1.mp3',
            'content_type': 'audio/mpeg'
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_2_Bellingham_Castle_Tour_1760630519083.mp3',
            's3_key': 'listening/academic/test-1/audio/section2.mp3',
            'content_type': 'audio/mpeg'
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_3_Renewable_Energy_Research_Project_1760630519083.mp3',
            's3_key': 'listening/academic/test-1/audio/section3.mp3',
            'content_type': 'audio/mpeg'
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_4_Lecture_1760630519082.mp3',
            's3_key': 'listening/academic/test-1/audio/section4.mp3',
            'content_type': 'audio/mpeg'
        },
        {
            'local': 'attached_assets/Academic_Listening_Test_1_Section_2_Map_1760630519083.png',
            's3_key': 'listening/academic/test-1/images/section2_castle_map.png',
            'content_type': 'image/png'
        }
    ]
    
    uploaded = 0
    failed = 0
    
    print(f"\n📤 Uploading files to S3 bucket '{bucket_name}'...")
    
    for file_info in files_to_upload:
        local_path = file_info['local']
        s3_key = file_info['s3_key']
        content_type = file_info['content_type']
        
        if os.path.exists(local_path):
            try:
                # Upload file with appropriate metadata
                with open(local_path, 'rb') as file:
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=s3_key,
                        Body=file,
                        ContentType=content_type,
                        CacheControl='max-age=31536000',  # Cache for 1 year
                        Metadata={
                            'test': 'academic-listening-test-1',
                            'type': 'audio' if 'audio' in content_type else 'image'
                        }
                    )
                
                print(f"  ✓ Uploaded: {s3_key}")
                uploaded += 1
                
            except Exception as e:
                print(f"  ✗ Failed to upload {local_path}: {e}")
                failed += 1
        else:
            print(f"  ✗ File not found: {local_path}")
            failed += 1
    
    return uploaded, failed

def generate_presigned_urls(bucket_name):
    """Generate pre-signed URLs for accessing private S3 objects"""
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    
    # Define objects to generate URLs for
    objects = [
        'listening/academic/test-1/audio/section1.mp3',
        'listening/academic/test-1/audio/section2.mp3',
        'listening/academic/test-1/audio/section3.mp3',
        'listening/academic/test-1/audio/section4.mp3',
        'listening/academic/test-1/images/section2_castle_map.png'
    ]
    
    urls = {}
    print("\n🔗 Generating pre-signed URLs for test access...")
    
    for obj_key in objects:
        try:
            # Generate URL valid for 7 days
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': obj_key},
                ExpiresIn=604800  # 7 days
            )
            urls[obj_key] = url
            print(f"  ✓ Generated URL for: {obj_key.split('/')[-1]}")
        except Exception as e:
            print(f"  ✗ Failed to generate URL for {obj_key}: {e}")
    
    return urls

def main():
    """Main function to set up S3 and upload files"""
    print("=" * 60)
    print("🚀 SETTING UP S3 STORAGE FOR IELTS LISTENING TESTS")
    print("=" * 60)
    print(f"Region: {AWS_REGION}")
    print()
    
    # Create S3 bucket (private)
    bucket_name = create_s3_bucket_private()
    
    if bucket_name:
        # Upload files
        uploaded, failed = upload_listening_test_files(bucket_name)
        
        # Generate pre-signed URLs
        if uploaded > 0:
            urls = generate_presigned_urls(bucket_name)
            
            # Summary
            print("\n" + "=" * 60)
            print("✅ S3 SETUP COMPLETE")
            print("=" * 60)
            print(f"\n📦 S3 Bucket: {bucket_name}")
            print(f"📤 Files uploaded: {uploaded}")
            print(f"❌ Files failed: {failed}")
            print(f"🔗 Pre-signed URLs generated: {len(urls)}")
            
            print("\n📝 Note: The bucket is private. Files are accessed via:")
            print("  • Pre-signed URLs (temporary access)")
            print("  • IAM credentials (permanent access)")
            print("  • CloudFront distribution (optional, for CDN)")
            
            return {
                'success': True,
                'bucket': bucket_name,
                'uploaded': uploaded,
                'failed': failed,
                'urls': list(urls.keys())
            }
    else:
        print("\n❌ Failed to create S3 bucket")
        return {'success': False}

if __name__ == "__main__":
    result = main()
    import json
    print(f"\n📄 Result: {json.dumps(result, indent=2)}")