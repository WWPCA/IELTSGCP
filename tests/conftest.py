"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from playwright.sync_api import sync_playwright

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def playwright():
    """Provide Playwright instance for E2E tests"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright):
    """Provide browser instance"""
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Provide page instance"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def test_database_url():
    """Provide test database URL"""
    return os.getenv('TEST_DATABASE_URL', 'postgresql://localhost/ielts_ai_prep_test')


@pytest.fixture(scope="session")
def google_cloud_project():
    """Provide Google Cloud project ID"""
    return os.getenv('GOOGLE_CLOUD_PROJECT')


@pytest.fixture(scope="session")
def gemini_api_key():
    """Provide Gemini API key"""
    return os.getenv('GEMINI_API_KEY')


# GDPR Testing Fixtures
@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app import app as flask_app
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    yield flask_app


@pytest.fixture
def db_connection():
    """Create database connection for testing"""
    from gcp.firestore_dal import FirestoreConnection
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'test-project')
    environment = 'test'
    return FirestoreConnection(project_id=project_id, environment=environment)


@pytest.fixture
def user_dal(db_connection):
    """Create UserDAL for testing"""
    from gcp.firestore_dal import UserDAL
    return UserDAL(db_connection)


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests requiring external services")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance and benchmark tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "smoke: Smoke tests for deployed environment")
    config.addinivalue_line("markers", "benchmark: Performance benchmark tests")
    config.addinivalue_line("markers", "gdpr: GDPR compliance tests")
