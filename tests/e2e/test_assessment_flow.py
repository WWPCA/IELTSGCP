"""
End-to-end tests for complete assessment workflows
"""
import os
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestWritingAssessmentFlow:
    """E2E tests for writing assessment workflow"""
    
    def test_complete_writing_assessment_flow(self, page: Page):
        """Test complete writing assessment from start to results"""
        # Navigate to login page
        page.goto("http://localhost:5000/login")
        
        # Login with test credentials from environment
        test_email = os.environ.get('TEST_USER_EMAIL', 'test@example.com')
        test_password = os.environ.get('TEST_USER_PASSWORD', 'DefaultTestPass123!')
        page.fill('input[name="email"]', test_email)
        page.fill('input[name="password"]', test_password)
        page.click('button[type="submit"]')
        
        # Wait for redirect to dashboard
        page.wait_for_url("**/dashboard")
        expect(page).to_have_title(/Dashboard/)
        
        # Navigate to writing assessment
        page.click('text=Start Writing Assessment')
        
        # Select Academic Task 1
        page.click('text=Academic Task 1')
        
        # Fill in writing response
        task_response = """The graph shows the number of tourists visiting a Caribbean island between 2010 and 2017.
        
Overall, the total number of tourists increased significantly during this period, with cruise ship visitors showing more growth than those staying on the island.

In 2010, approximately 0.75 million tourists stayed on the island while about 0.25 million stayed on cruise ships. Both categories grew steadily, with island visitors peaking at 1.5 million in 2013.

By 2017, cruise ship tourists had increased dramatically to 2 million, surpassing island-staying tourists who remained at approximately 1.5 million. The total number of visitors reached about 3.5 million by the end of the period."""
        
        page.fill('textarea[name="response"]', task_response)
        
        # Submit assessment
        page.click('button:has-text("Submit for Evaluation")')
        
        # Wait for results
        page.wait_for_selector('.assessment-results', timeout=60000)
        
        # Verify results contain all criteria
        expect(page.locator('text=Overall Band')).to_be_visible()
        expect(page.locator('text=Task Achievement')).to_be_visible()
        expect(page.locator('text=Coherence and Cohesion')).to_be_visible()
        expect(page.locator('text=Lexical Resource')).to_be_visible()
        expect(page.locator('text=Grammatical Range')).to_be_visible()
        expect(page.locator('text=Personalized Improvement Plan')).to_be_visible()


@pytest.mark.e2e
class TestSpeakingAssessmentFlow:
    """E2E tests for speaking assessment workflow"""
    
    def test_complete_speaking_assessment_flow(self, page: Page):
        """Test complete speaking assessment from start to results"""
        # Navigate to login page
        page.goto("http://localhost:5000/login")
        
        # Login with test credentials from environment
        test_email = os.environ.get('TEST_USER_EMAIL', 'test@example.com')
        test_password = os.environ.get('TEST_USER_PASSWORD', 'DefaultTestPass123!')
        page.fill('input[name="email"]', test_email)
        page.fill('input[name="password"]', test_password)
        page.click('button[type="submit"]')
        
        # Navigate to speaking assessment
        page.click('text=Start Speaking Assessment')
        
        # Grant microphone permission (in test environment)
        # Note: This requires proper browser context setup
        
        # Verify Maya introduction
        expect(page.locator('text=Maya')).to_be_visible()
        expect(page.locator('text=IELTS examiner')).to_be_visible()
        
        # Verify assessment sections are available
        expect(page.locator('text=Part 1')).to_be_visible()
        expect(page.locator('text=Part 2')).to_be_visible()
        expect(page.locator('text=Part 3')).to_be_visible()


@pytest.mark.e2e
class TestUserRegistrationFlow:
    """E2E tests for user registration workflow"""
    
    def test_new_user_registration(self, page: Page):
        """Test new user registration flow"""
        page.goto("http://localhost:5000/register")
        
        # Fill registration form
        page.fill('input[name="email"]', f'newuser_{int(page.evaluate("Date.now()"))}@example.com')
        page.fill('input[name="password"]', 'SecurePassword123!')
        page.fill('input[name="confirm_password"]', 'SecurePassword123!')
        
        # Solve reCAPTCHA (mocked in test environment)
        
        # Submit
        page.click('button[type="submit"]')
        
        # Verify success
        expect(page.locator('text=Registration successful')).to_be_visible()
