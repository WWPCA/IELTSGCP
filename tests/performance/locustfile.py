"""
Load testing with Locust
"""
from locust import HttpUser, task, between
import json


class IELTSAIPrepUser(HttpUser):
    """Simulated user for load testing"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tasks"""
        self.client.post("/api/login", json={
            "email": "loadtest@example.com",
            "password": "LoadTest123!"
        })
    
    @task(3)
    def view_homepage(self):
        """Load homepage"""
        self.client.get("/")
    
    @task(2)
    def view_dashboard(self):
        """Load user dashboard"""
        self.client.get("/dashboard")
    
    @task(1)
    def submit_writing_assessment(self):
        """Submit a writing assessment"""
        response = """The graph shows trends in tourism from 2010 to 2017.
        
Overall, tourist numbers increased significantly, with cruise ship visitors showing dramatic growth.

In 2010, 0.75 million tourists stayed on the island while 0.25 million stayed on cruise ships. Both categories grew steadily.

By 2017, cruise ship tourists reached 2 million, surpassing island visitors at 1.5 million."""
        
        self.client.post("/api/assessments/writing", json={
            "type": "academic_task1",
            "response": response
        })
    
    @task(1)
    def get_assessment_results(self):
        """Retrieve assessment results"""
        self.client.get("/api/assessments/12345/results")
