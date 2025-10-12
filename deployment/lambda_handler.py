"""
Lambda Handler for IELTS AI Prep Flask Application
Wraps Flask app using awsgi for Lambda compatibility
"""

import os
import sys

# Ensure all modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import awsgi

# Create Lambda handler using awsgi (for WSGI Flask apps)
def handler(event, context):
    return awsgi.response(app, event, context)

# For local testing
if __name__ == "__main__":
    app.run(debug=True, port=5000)
