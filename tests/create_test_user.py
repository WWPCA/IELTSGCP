#!/usr/bin/env python3
"""
Test User Creation Utility for GDPR Testing
Creates test users for automated and manual GDPR compliance testing
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gcp.firestore_dal import FirestoreConnection, UserDAL

# Test user credentials
TEST_USERS = [
    {
        'username': 'gdprtest',
        'email': 'gdpr_test@example.com',
        'password': 'GDPRTest123!',
        'full_name': 'GDPR Test User'
    },
    {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'full_name': 'Test User'
    },
    {
        'username': 'manualtest',
        'email': 'manual@example.com',
        'password': 'ManualTest123!',
        'full_name': 'Manual Test User'
    }
]

def create_test_users(environment='test'):
    """Create test users for GDPR testing"""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'test-project')
    
    print(f"🔧 Creating test users in environment: {environment}")
    print(f"📦 Project ID: {project_id}\n")
    
    db_connection = FirestoreConnection(project_id=project_id, environment=environment)
    user_dal = UserDAL(db_connection)
    
    created_count = 0
    existing_count = 0
    
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
    
    print("\n📝 Test Credentials:")
    print("=" * 50)
    for user_info in TEST_USERS:
        print(f"\nEmail:    {user_info['email']}")
        print(f"Password: {user_info['password']}")
        print(f"Purpose:  {'Automated GDPR tests' if 'gdpr' in user_info['email'] else 'Manual testing'}")
    print("=" * 50)

def delete_test_users(environment='test'):
    """Delete test users (cleanup)"""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'test-project')
    
    print(f"🗑️  Deleting test users from environment: {environment}")
    
    db_connection = FirestoreConnection(project_id=project_id, environment=environment)
    user_dal = UserDAL(db_connection)
    
    for user_info in TEST_USERS:
        try:
            if user_dal.delete_user(user_info['email']):
                print(f"✅ Deleted user: {user_info['email']}")
            else:
                print(f"ℹ️  User not found: {user_info['email']}")
        except Exception as e:
            print(f"❌ Error deleting {user_info['email']}: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage test users for GDPR testing')
    parser.add_argument('action', choices=['create', 'delete'], help='Action to perform')
    parser.add_argument('--env', default='test', help='Environment (test, development, production)')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        create_test_users(args.env)
    elif args.action == 'delete':
        delete_test_users(args.env)
