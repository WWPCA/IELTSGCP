"""
⚠️ DEPRECATED - Firestore Integration Tests (Not Used)

These tests are for the deprecated GCP Firestore implementation.
The platform now uses AWS DynamoDB. See tests for DynamoDB instead.

Integration tests for Firestore database operations (DEPRECATED)
"""
import pytest
import os
from datetime import datetime
from google.cloud import firestore


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv('GOOGLE_CLOUD_PROJECT'), reason="GOOGLE_CLOUD_PROJECT not set")
class TestFirestoreIntegration:
    """Integration tests for Firestore operations"""
    
    @pytest.fixture
    def db(self):
        """Create Firestore client"""
        return firestore.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
    
    def test_create_user_document(self, db):
        """Test creating a user document in Firestore"""
        test_user_id = f"test_user_{datetime.utcnow().timestamp()}"
        user_ref = db.collection('test_users').document(test_user_id)
        
        user_data = {
            'email': 'test@example.com',
            'created_at': firestore.SERVER_TIMESTAMP,
            'active_assessments': 0
        }
        
        user_ref.set(user_data)
        
        # Verify
        doc = user_ref.get()
        assert doc.exists
        assert doc.to_dict()['email'] == 'test@example.com'
        
        # Cleanup
        user_ref.delete()
    
    def test_create_assessment_document(self, db):
        """Test creating an assessment document"""
        test_assessment_id = f"test_assessment_{datetime.utcnow().timestamp()}"
        assessment_ref = db.collection('test_assessments').document(test_assessment_id)
        
        assessment_data = {
            'user_id': 'test_user_123',
            'type': 'academic_writing',
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        assessment_ref.set(assessment_data)
        
        # Verify
        doc = assessment_ref.get()
        assert doc.exists
        assert doc.to_dict()['type'] == 'academic_writing'
        
        # Cleanup
        assessment_ref.delete()
    
    def test_query_assessments_by_user(self, db):
        """Test querying assessments by user ID"""
        # Create test data
        test_user_id = f"test_user_{datetime.utcnow().timestamp()}"
        
        for i in range(3):
            assessment_ref = db.collection('test_assessments').document(f"assessment_{i}")
            assessment_ref.set({
                'user_id': test_user_id,
                'type': 'writing',
                'created_at': firestore.SERVER_TIMESTAMP
            })
        
        # Query
        assessments = db.collection('test_assessments').where('user_id', '==', test_user_id).stream()
        count = sum(1 for _ in assessments)
        
        assert count == 3
        
        # Cleanup
        for i in range(3):
            db.collection('test_assessments').document(f"assessment_{i}").delete()
