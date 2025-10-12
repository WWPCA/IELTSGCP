#!/usr/bin/env python3
"""
Test User Creation Utility for GDPR Testing
Creates test users for automated and manual GDPR compliance testing
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gcp.firestore_dal import FirestoreConnection, UserDAL

# Test user configuration from environment variables
def get_test_users():
    """Get test user configuration from environment variables"""
    # Default test users if environment variables not set
    # These are intentionally generic and should be overridden via env vars
    return [
        {
            'username': os.environ.get('GDPR_TEST_USERNAME', 'gdprtest'),
            'email': os.environ.get('GDPR_TEST_EMAIL', 'gdpr_test@example.com'),
            'password': os.environ.get('GDPR_TEST_PASSWORD', os.urandom(16).hex()),
            'full_name': 'GDPR Test User'
        },
        {
            'username': os.environ.get('TEST_USER_USERNAME', 'testuser'),
            'email': os.environ.get('TEST_USER_EMAIL', 'test@example.com'),
            'password': os.environ.get('TEST_USER_PASSWORD', os.urandom(16).hex()),
            'full_name': 'Test User'
        },
        {
            'username': os.environ.get('MANUAL_TEST_USERNAME', 'manualtest'),
            'email': os.environ.get('MANUAL_TEST_EMAIL', 'manual@example.com'),
            'password': os.environ.get('MANUAL_TEST_PASSWORD', os.urandom(16).hex()),
            'full_name': 'Manual Test User'
        }
    ]

def create_test_users(environment='test'):
    """Create test users for GDPR testing"""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'test-project')
    
    print(f"🔧 Creating test users in environment: {environment}")
    print(f"📦 Project ID: {project_id}\n")
    
    # Check if test passwords are configured
    if not os.environ.get('GDPR_TEST_PASSWORD'):
        print("⚠️  Warning: Test passwords not configured in environment variables.")
        print("   Random passwords will be generated. Set the following env vars:")
        print("   - GDPR_TEST_PASSWORD")
        print("   - TEST_USER_PASSWORD")
        print("   - MANUAL_TEST_PASSWORD\n")
    
    db_connection = FirestoreConnection(project_id=project_id, environment=environment)
    user_dal = UserDAL(db_connection)
    
    created_count = 0
    existing_count = 0
    
    TEST_USERS = get_test_users()
    
    for user_info in TEST_USERS:
        try:
            user = user_dal.create_user(
                username=user_info['username'],
                email=user_info['email'],
                password=user_info['password'],
                full_name=user_info['full_name']
            )
            print(f"✅ Created user: {user_info['email']}")
            created_count += 1
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"ℹ️  User already exists: {user_info['email']}")
                existing_count += 1
            else:
                print(f"❌ Error creating {user_info['email']}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Created: {created_count}")
    print(f"   Existing: {existing_count}")
    print(f"   Total: {len(TEST_USERS)}")
    
    print("\n📝 Test User Emails:")
    print("=" * 50)
    for user_info in TEST_USERS:
        print(f"\nEmail:    {user_info['email']}")
        print(f"Purpose:  {'Automated GDPR tests' if 'gdpr' in user_info['email'] else 'Manual testing'}")
    print("\nNote: Passwords are stored in environment variables for security")

def delete_test_users(environment='test'):
    """Delete test users from the database"""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'test-project')
    
    print(f"🗑️  Deleting test users from environment: {environment}")
    print(f"📦 Project ID: {project_id}\n")
    
    db_connection = FirestoreConnection(project_id=project_id, environment=environment)
    user_dal = UserDAL(db_connection)
    
    deleted_count = 0
    TEST_USERS = get_test_users()
    
    for user_info in TEST_USERS:
        try:
            user_dal.delete_user(user_info['email'])
            print(f"✅ Deleted user: {user_info['email']}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Error deleting {user_info['email']}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Deleted: {deleted_count}")
    print(f"   Total: {len(TEST_USERS)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test User Management for GDPR Testing')
    parser.add_argument('action', choices=['create', 'delete'], help='Action to perform')
    parser.add_argument('--env', default='test', help='Environment (test/development)')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        create_test_users(args.env)
    elif args.action == 'delete':
        delete_test_users(args.env)