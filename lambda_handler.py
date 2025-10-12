"""
Lambda Handler for IELTS AI Prep Flask Application
Wraps Flask app using Mangum for Lambda compatibility
"""

import os
import sys

# Ensure all modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from mangum import Mangum
from app import app

# Create Lambda handler
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    app.run(debug=True, port=5000)
