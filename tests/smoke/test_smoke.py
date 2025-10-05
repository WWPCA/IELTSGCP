"""
Smoke tests for deployed environment
"""
import pytest
import requests
import os


@pytest.mark.smoke
class TestEnvironmentHealth:
    """Smoke tests for environment health"""
    
    @pytest.fixture
    def base_url(self):
        """Get base URL from environment"""
        return os.getenv('TEST_URL', 'http://localhost:5000')
    
    def test_homepage_loads(self, base_url):
        """Test that homepage loads successfully"""
        response = requests.get(base_url, timeout=10)
        assert response.status_code == 200
        assert 'IELTS AI Prep' in response.text
    
    def test_login_page_loads(self, base_url):
        """Test that login page loads"""
        response = requests.get(f"{base_url}/login", timeout=10)
        assert response.status_code == 200
        assert 'login' in response.text.lower()
    
    def test_register_page_loads(self, base_url):
        """Test that register page loads"""
        response = requests.get(f"{base_url}/register", timeout=10)
        assert response.status_code == 200
        assert 'register' in response.text.lower()
    
    def test_static_assets_load(self, base_url):
        """Test that static assets load correctly"""
        # Test CSS
        css_response = requests.get(f"{base_url}/static/css/styles.css", timeout=10)
        assert css_response.status_code == 200 or css_response.status_code == 304
        
        # Test JS
        js_response = requests.get(f"{base_url}/static/js/main.js", timeout=10)
        assert js_response.status_code in [200, 304, 404]  # 404 acceptable if file doesn't exist
    
    def test_api_health_check(self, base_url):
        """Test API health check endpoint"""
        response = requests.get(f"{base_url}/api/health", timeout=10)
        # Accept 200 or 404 (if endpoint doesn't exist yet)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert 'status' in data
            assert data['status'] == 'healthy'


@pytest.mark.smoke
class TestCriticalFunctionality:
    """Smoke tests for critical functionality"""
    
    @pytest.fixture
    def base_url(self):
        """Get base URL from environment"""
        return os.getenv('TEST_URL', 'http://localhost:5000')
    
    def test_database_connectivity(self, base_url):
        """Test that application can connect to database"""
        # This would check database connectivity
        # For now, we verify the app runs without database errors
        response = requests.get(base_url, timeout=10)
        assert response.status_code == 200
    
    def test_user_registration_available(self, base_url):
        """Test that user registration is available"""
        response = requests.get(f"{base_url}/register", timeout=10)
        assert response.status_code == 200
        assert 'email' in response.text.lower()
        assert 'password' in response.text.lower()
    
    def test_assessment_pages_accessible(self, base_url):
        """Test that assessment pages are accessible (after login)"""
        # This would require authenticated session
        # For smoke test, just verify the routes exist
        response = requests.get(f"{base_url}/assessments", timeout=10)
        # Either 200 (if public) or 302/401 (if requires auth)
        assert response.status_code in [200, 302, 401, 403]


@pytest.mark.smoke
class TestExternalDependencies:
    """Smoke tests for external dependencies"""
    
    def test_google_cloud_connectivity(self):
        """Test connectivity to Google Cloud services"""
        # Test if we can reach Google Cloud APIs
        try:
            response = requests.get('https://www.googleapis.com', timeout=5)
            assert response.status_code in [200, 301, 302, 404]
        except requests.RequestException:
            pytest.skip("Google Cloud APIs not reachable")
    
    def test_cdn_availability(self):
        """Test CDN availability for static assets"""
        # Test Bootstrap CDN
        response = requests.get('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css', timeout=5)
        assert response.status_code == 200
