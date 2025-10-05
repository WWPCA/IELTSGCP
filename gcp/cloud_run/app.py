"""
IELTS GenAI Prep - Google Cloud Run Application
Migrated from AWS Lambda to Cloud Run with Firestore and Gemini
"""
from flask import Flask, send_from_directory, render_template, request, jsonify, redirect, url_for, session, flash
import json
import uuid
import time
import qrcode
import io
import base64
import secrets
import hashlib
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

# Import GCP services
from firestore_dal import FirestoreConnection, UserDAL, AssessmentDAL, SessionDAL, QRTokenDAL, EntitlementDAL
from gemini_live_service import GeminiLiveService, ContentModerationService
from gemini_service import GeminiService

# Real CSRF token generation
def csrf_token():
    return secrets.token_urlsafe(32)

# Production configuration
class ProductionConfig:
    RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_V2_SITE_KEY", "6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_V2_SECRET_KEY")
    GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = ProductionConfig()

# Disable caching for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Add cache buster for CSS/JS files
@app.context_processor
def inject_cache_buster():
    return dict(cache_buster=str(int(time.time())))

# Add no-cache headers
@app.after_request
def add_no_cache_headers(response):
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# Initialize Firestore and AI services
try:
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    region = os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')
    
    # Firestore
    db_connection = FirestoreConnection(project_id=project_id)
    user_dal = UserDAL(db_connection)
    assessment_dal = AssessmentDAL(db_connection)
    session_dal = SessionDAL(db_connection)
    qr_token_dal = QRTokenDAL(db_connection)
    entitlement_dal = EntitlementDAL(db_connection)
    
    # Gemini AI Services
    gemini_live = GeminiLiveService(project_id=project_id, region=region)
    gemini_service = GeminiService(project_id=project_id, region=region)
    content_moderation = ContentModerationService(project_id=project_id)
    
    print(f"[PRODUCTION] Connected to Firestore - project: {project_id}, region: {region}")
    use_production = True
    
except Exception as e:
    print(f"[ERROR] Failed to initialize GCP services: {e}")
    # Fallback to mock services for local development
    use_production = False
    db_connection = None
    user_dal = None

# Security headers and CORS
@app.after_request
def add_security_headers(response):
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    
    # CORS headers for mobile app support
    origin = request.headers.get('Origin')
    allowed_origins = [
        'capacitor://localhost',
        'http://localhost',
        'https://localhost',
        'ionic://localhost',
        'http://localhost:3000',
        'http://localhost:8100',
        'https://ieltsaiprep.com',
        'https://www.ieltsaiprep.com',
    ]
    
    if origin and origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response

# Health check endpoint for Cloud Run
@app.route('/health')
def health_check():
    """Health check for load balancer"""
    return jsonify({
        'status': 'healthy',
        'service': 'ielts-genai-prep',
        'region': os.environ.get('GOOGLE_CLOUD_REGION', 'unknown'),
        'version': os.environ.get('K_REVISION', 'dev')
    }), 200

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# TODO: Import all routes from original app.py
# This is a minimal starter - full migration requires copying all Flask routes

if __name__ == '__main__':
    # For local testing only
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
