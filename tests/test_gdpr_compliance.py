"""
GDPR Compliance Test Suite for IELTS AI Prep
Tests all GDPR data rights functionality including access, export, consent, and deletion
"""

import pytest
import json
import os
from flask import session
from datetime import datetime
from werkzeug.security import check_password_hash

# Test user credentials from environment variables
TEST_USER = {
    'email': os.environ.get('GDPR_TEST_EMAIL', 'gdpr_test@example.com'),
    'username': os.environ.get('GDPR_TEST_USERNAME', 'gdprtest'),
    'password': os.environ.get('GDPR_TEST_PASSWORD', 'DefaultTestPass123!'),
    'full_name': 'GDPR Test User'
}

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def authenticated_client(client, user_dal):
    """Create authenticated test client with logged-in user"""
    # Create test user
    try:
        user_dal.create_user(
            username=TEST_USER['username'],
            email=TEST_USER['email'],
            password=TEST_USER['password'],
            full_name=TEST_USER['full_name']
        )
    except Exception as e:
        if 'already exists' not in str(e):
            raise
    
    # Login
    with client.session_transaction() as sess:
        sess['user_email'] = TEST_USER['email']
        sess['logged_in'] = True
    
    yield client
    
    # Cleanup
    try:
        user_dal.delete_user(TEST_USER['email'])
    except:
        pass

class TestGDPRDataAccess:
    """Test GDPR Right to Access"""
    
    def test_my_data_page_requires_authentication(self, client):
        """Test that /gdpr/my-data requires login"""
        response = client.get('/gdpr/my-data')
        assert response.status_code == 302  # Redirect to login
        assert '/login' in response.location
    
    def test_my_data_page_displays_user_info(self, authenticated_client):
        """Test that authenticated users can view their data"""
        response = authenticated_client.get('/gdpr/my-data')
        assert response.status_code == 200
        assert TEST_USER['email'].encode() in response.data
        assert TEST_USER['username'].encode() in response.data

class TestGDPRDataExport:
    """Test GDPR Right to Data Portability"""
    
    def test_export_requires_authentication(self, client):
        """Test that data export requires login"""
        response = client.post('/gdpr/export-data')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Not authenticated'
    
    def test_export_returns_complete_user_data(self, authenticated_client):
        """Test that export includes all personal data"""
        response = authenticated_client.post('/gdpr/export-data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Verify all required sections are present
        assert 'personal_information' in data
        assert 'account_information' in data
        assert 'consent_preferences' in data
        assert 'assessment_information' in data
        assert 'export_metadata' in data
        
        # Verify personal information
        assert data['personal_information']['email'] == TEST_USER['email']
        assert data['personal_information']['username'] == TEST_USER['username']
        assert data['personal_information']['full_name'] == TEST_USER['full_name']
        
        # Verify export metadata
        assert data['export_metadata']['export_format'] == 'JSON'
        assert 'export_date' in data['export_metadata']
    
    def test_export_excludes_password_hash(self, authenticated_client):
        """Test that password hash is never exported"""
        response = authenticated_client.post('/gdpr/export-data')
        data = json.loads(response.data)
        
        # Convert to string to check entire export
        export_str = json.dumps(data)
        assert 'password' not in export_str.lower()
        assert 'password_hash' not in export_str.lower()

class TestGDPRConsentManagement:
    """Test GDPR Right to Withdraw Consent"""
    
    def test_consent_update_requires_authentication(self, client):
        """Test that consent update requires login"""
        response = client.post('/gdpr/update-consent',
                              json={'marketing_consent': True})
        assert response.status_code == 401
    
    def test_update_marketing_consent(self, authenticated_client, user_dal):
        """Test updating marketing consent preference"""
        # Update consent
        response = authenticated_client.post('/gdpr/update-consent',
                                            json={'marketing_consent': True,
                                                  'analytics_consent': False})
        assert response.status_code == 200
        
        # Verify consent was saved
        user = user_dal.get_user_by_email(TEST_USER['email'])
        assert user['preferences']['marketing_consent'] == True
        assert user['preferences']['analytics_consent'] == False
    
    def test_consent_withdrawal(self, authenticated_client, user_dal):
        """Test withdrawing all consents"""
        # Withdraw all consent
        response = authenticated_client.post('/gdpr/update-consent',
                                            json={'marketing_consent': False,
                                                  'analytics_consent': False})
        assert response.status_code == 200
        
        # Verify withdrawal
        user = user_dal.get_user_by_email(TEST_USER['email'])
        assert user['preferences']['marketing_consent'] == False
        assert user['preferences']['analytics_consent'] == False

class TestGDPRAccountDeletion:
    """Test GDPR Right to Erasure"""
    
    def test_deletion_requires_authentication(self, client):
        """Test that account deletion requires login"""
        response = client.post('/gdpr/delete-account',
                              json={'password': 'test'})
        assert response.status_code == 401
    
    def test_deletion_requires_password(self, authenticated_client):
        """Test that deletion requires password confirmation"""
        response = authenticated_client.post('/gdpr/delete-account',
                                             json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Password required'
    
    def test_deletion_validates_password(self, authenticated_client):
        """Test that deletion validates password"""
        response = authenticated_client.post('/gdpr/delete-account',
                                             json={'password': 'WrongPassword'})
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid password'
    
    def test_successful_account_deletion(self, authenticated_client, user_dal):
        """Test successful account deletion removes all data"""
        # Delete account
        response = authenticated_client.post('/gdpr/delete-account',
                                             json={'password': TEST_USER['password']})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Verify user is deleted
        user = user_dal.get_user_by_email(TEST_USER['email'])
        assert user is None
    
    def test_deletion_clears_session(self, authenticated_client):
        """Test that account deletion clears user session"""
        response = authenticated_client.post('/gdpr/delete-account',
                                             json={'password': TEST_USER['password']})
        assert response.status_code == 200
        
        # Verify session is cleared (try to access protected page)
        response = authenticated_client.get('/gdpr/my-data')
        assert response.status_code == 302  # Redirect to login

class TestGDPRPrivacyPolicy:
    """Test Privacy Policy Section 8 Compliance"""
    
    def test_privacy_policy_section_8_exists(self, client):
        """Test that Privacy Policy section 8 exists and contains data rights"""
        response = client.get('/privacy-policy')
        assert response.status_code == 200
        
        # Check for section 8
        assert b'8. Your Data Protection Rights' in response.data or \
               b'Your Data Protection Rights' in response.data
        
        # Check for GDPR rights
        assert b'Right to Access' in response.data
        assert b'Right to Erasure' in response.data
        assert b'Right to Data Portability' in response.data
        assert b'Right to Object' in response.data
    
    def test_privacy_policy_links_to_gdpr_dashboard(self, client):
        """Test that Privacy Policy links to GDPR dashboard"""
        response = client.get('/privacy-policy')
        assert b'/gdpr/my-data' in response.data or \
               b'Data Rights Dashboard' in response.data

class TestGDPRCompliance:
    """Overall GDPR compliance tests"""
    
    def test_helpdesk_email_visible(self, client):
        """Test that helpdesk email is visible for GDPR requests"""
        response = client.get('/privacy-policy')
        assert b'helpdesk@ieltsaiprep.com' in response.data
    
    def test_30_day_response_commitment(self, client):
        """Test that 30-day response time is documented"""
        response = client.get('/privacy-policy')
        assert b'30 days' in response.data or b'30-day' in response.data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
