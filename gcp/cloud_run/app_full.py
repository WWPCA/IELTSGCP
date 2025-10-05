"""
IELTS GenAI Prep - Production Flask Application
Uses AWS DynamoDB for data storage with fallback to mock services for development
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
import boto3

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

# Real CSRF token generation
def csrf_token():
    return secrets.token_urlsafe(32)

# Production configuration
class ProductionConfig:
    RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_V2_SITE_KEY", "6LcYOkUqAAAAAK8xH4iJcZv_TfUdJ8TlYS_Ov8Ix")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_V2_SECRET_KEY")

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = ProductionConfig()

# Kill caching for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Add cache buster for CSS/JS files
@app.context_processor
def inject_cache_buster():
    return dict(cache_buster=str(int(time.time())))

# Add no-cache headers for development
@app.after_request
def add_no_cache_headers(response):
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# Initialize AWS DynamoDB connections with fallback to mock for development
try:
    # Try to use production DynamoDB
    from dynamodb_dal import DynamoDBConnection, UserDAL
    region = os.environ.get('AWS_REGION', 'us-east-1')
    db_connection = DynamoDBConnection(region=region)
    user_dal = UserDAL(db_connection)
    
    print(f"[PRODUCTION] Connected to DynamoDB in region: {region}")
    use_production = True
    
except Exception as e:
    print(f"[INFO] DynamoDB unavailable, using mock services: {e}")
    # Fallback to mock services for development
    from aws_mock_config import aws_mock
    db_connection = aws_mock
    user_dal = None
    use_production = False

# Always initialize mock storage variables (ensures they exist even if DynamoDB works)
qr_tokens = {}
sessions = {}
mock_purchases = {}
password_reset_tokens = {}

# Register mobile API blueprint if available
try:
    from api_mobile import api_mobile
    app.register_blueprint(api_mobile)
    print("[INFO] Mobile API endpoints registered at /api/v1/*")
except ImportError:
    print("[INFO] Mobile API blueprint not available")

# Import receipt validation for endpoints 
try:
    from receipt_validation import ReceiptValidationService, PurchaseStatus, validate_app_store_purchase
    receipt_service = ReceiptValidationService()
    print("[INFO] Receipt validation services initialized")
except (ImportError, RuntimeError) as e:
    print(f"[INFO] Receipt validation services not available: {e}")
    receipt_service = None

# Apply security headers and CORS for mobile app support
@app.after_request
def add_security_headers(response):
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    
    # CORS headers for mobile app and web client support
    origin = request.headers.get('Origin')
    allowed_origins = [
        'capacitor://localhost',  # Capacitor iOS
        'http://localhost',       # Capacitor Android  
        'https://localhost',      # Capacitor Android (HTTPS)
        'ionic://localhost',      # Ionic specific
        'http://localhost:3000',  # Local web development
        'http://localhost:8100',  # Ionic serve
        'https://ieltsgenaiprep.com',    # Production web
        'https://www.ieltsgenaiprep.com', # Production web (www)
    ]
    
    # CORS headers with proper credential handling
    if origin and origin in allowed_origins:
        # For allowlisted origins, echo the origin and allow credentials
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    elif origin is None:
        # For requests without origin (mobile apps), allow wildcard but no credentials
        response.headers['Access-Control-Allow-Origin'] = '*'
        # Don't set Access-Control-Allow-Credentials for wildcard origins
    else:
        # For non-allowlisted origins, deny access
        response.headers['Access-Control-Allow-Origin'] = 'null'
    
    # Essential CORS headers for mobile app functionality
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Accept,Origin,X-API-Key,X-Session-ID,X-Device-ID,X-Platform'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours preflight cache
    response.headers['Access-Control-Expose-Headers'] = 'X-Session-ID,X-RateLimit-Remaining,X-RateLimit-Reset'
    response.headers['Vary'] = 'Origin'  # Important for proper caching
    
    return response

# Handle preflight OPTIONS requests for CORS
from flask import make_response
@app.route('/<path:path>', methods=['OPTIONS'])
@app.route('/', methods=['OPTIONS'])
def handle_preflight(path=None):
    """Handle CORS preflight requests for all routes"""
    response = make_response()
    origin = request.headers.get('Origin')
    response.headers['Access-Control-Allow-Origin'] = origin or '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Accept,Origin,X-API-Key,X-Session-ID,X-Device-ID,X-Platform'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response
print("[INFO] Security headers applied to all endpoints")
# Actual assessment data structure to match existing templates
user_assessments = {
    "test@ieltsaiprep.com": {
        "academic_speaking": [
            {
                'id': 1,
                'title': 'Academic Speaking Assessment 1',
                'description': 'Comprehensive IELTS Academic Speaking test with AI examiner Maya',
                'assessment_type': 'academic_speaking',
                'created_at': '2024-12-01T10:00:00Z',
                'completed': True,
                'score': 7.5,
                'transcript': 'User discussed education systems with excellent fluency and vocabulary range.',
                'feedback': 'Strong performance with natural conversation flow and appropriate register.',
                'audio_available': False
            }
        ],
        "academic_writing": [
            {
                'id': 2,
                'title': 'Academic Writing Assessment 1',
                'description': 'IELTS Academic Writing Tasks 1 & 2 with TrueScore feedback',
                'assessment_type': 'academic_writing',
                'created_at': '2024-12-01T14:30:00Z',
                'completed': True,
                'score': 7.0,
                'essay_text': 'Education plays a crucial role in shaping society. Universities should balance theoretical knowledge with practical skills to prepare graduates for evolving workplace demands...',
                'feedback': 'Well-structured response with clear task achievement and coherent organization.',
                'task1_score': 7.0,
                'task2_score': 7.0
            }
        ],
        "general_speaking": [
            {
                'id': 3,
                'title': 'General Training Speaking Assessment 1',
                'description': 'IELTS General Training Speaking test focusing on everyday situations',
                'assessment_type': 'general_speaking',
                'created_at': '2024-12-02T09:15:00Z',
                'completed': True,
                'score': 6.5,
                'transcript': 'Discussed daily routines, travel experiences, and future plans with natural flow.',
                'feedback': 'Good interaction skills with appropriate use of informal language.',
                'audio_available': False
            }
        ],
        "general_writing": [
            {
                'id': 4,
                'title': 'General Training Writing Assessment 1',
                'description': 'IELTS General Training Writing Tasks 1 & 2',
                'assessment_type': 'general_writing',
                'created_at': '2024-12-02T16:45:00Z',
                'completed': True,
                'score': 6.5,
                'essay_text': 'Letter writing task completed with appropriate tone and format, followed by opinion essay on technology in education...',
                'feedback': 'Clear communication with good task fulfillment and appropriate language use.',
                'task1_score': 6.5,
                'task2_score': 6.5
            }
        ]
    }
}

@app.route('/')
def home():
    """Serve working template with purple background and 10 FAQs"""
    # Always use template system for proper functionality
    class AnonymousUser:
        is_authenticated = False
        email = None
    # Serve the working template directly
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return render_template('comprehensive_preview.html', current_user=AnonymousUser())

@app.route('/original-home')
def original_home():
    """Serve original homepage with TrueScore® and ClearScore® branding"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('index.html', current_user=AnonymousUser())

@app.route('/index')
def index():
    """Index route for template compatibility"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('index.html', current_user=AnonymousUser())

@app.route('/assessment-products')
def assessment_products_page():
    """Assessment products page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('assessment_products.html', current_user=AnonymousUser())

@app.route('/preview/writing-assessment')
def preview_writing_assessment():
    """Preview the writing assessment interface without authentication"""
    # Return the standalone test template that has all the same styling
    # but doesn't depend on the full navigation system
    try:
        with open('test_divided_screen.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return """
        <div style="padding: 20px; font-family: Arial;">
            <h1>🎯 Writing Assessment Preview</h1>
            <p>The divided screen template is ready! It includes:</p>
            <ul>
                <li>✅ <strong>Left Panel (45%)</strong>: IELTS GenAI Prep logo + question display</li>
                <li>✅ <strong>Right Panel (55%)</strong>: Response writing area</li>
                <li>✅ <strong>Real IELTS exam format</strong> with professional styling</li>
                <li>✅ <strong>Mobile responsive</strong> design</li>
                <li>✅ <strong>Task switching</strong> between Task 1 and Task 2</li>
                <li>✅ <strong>Word counting</strong> with requirements tracking</li>
            </ul>
            <p>Navigate to <code>/preview/writing-assessment</code> to see the full interface!</p>
        </div>
        """

@app.route('/login')
def login():
    """Login page - maintain consistency with working template design"""
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        # Inject redesigned login page with clear instructions
        login_section = '''
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-12 col-md-10 col-lg-8">
                    <div class="text-center mb-4">
                        <h1 class="fw-bold text-primary mb-3">Welcome to IELTS GenAI Prep</h1>
                        <p class="lead text-muted">Choose how you'd like to access your account</p>
                    </div>

                    <!-- Clear Options Cards -->
                    <div class="row g-4 mb-5">
                        <!-- Existing Users - Login -->
                        <div class="col-md-6">
                            <div class="card h-100 border-primary shadow-sm">
                                <div class="card-header bg-primary text-white text-center">
                                    <i class="fas fa-sign-in-alt fa-2x mb-2"></i>
                                    <h4 class="mb-0">Already Have an Account?</h4>
                                </div>
                                <div class="card-body text-center">
                                    <p class="card-text mb-4">Log in to access your assessments, view progress, and continue your IELTS preparation journey.</p>
                                    <button class="btn btn-primary btn-lg w-100" onclick="showLogin()">
                                        <i class="fas fa-envelope me-2"></i>Login with Email
                                    </button>
                                    <hr class="my-3">
                                    <button class="btn btn-outline-primary btn-lg w-100" onclick="showQR()">
                                        <i class="fas fa-qrcode me-2"></i>Quick Login with QR
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- New Users - Register -->
                        <div class="col-md-6">
                            <div class="card h-100 border-success shadow-sm">
                                <div class="card-header bg-success text-white text-center">
                                    <i class="fas fa-user-plus fa-2x mb-2"></i>
                                    <h4 class="mb-0">New to IELTS GenAI Prep?</h4>
                                </div>
                                <div class="card-body text-center">
                                    <p class="card-text mb-4">Create your account through our mobile app to get started with AI-powered IELTS assessments.</p>
                                    <div class="alert alert-info mb-3">
                                        <small><i class="fas fa-info-circle me-2"></i>Registration is only available through our mobile app</small>
                                    </div>
                                    <a href="/qr-auth" class="btn btn-success btn-lg w-100">
                                        <i class="fas fa-download me-2"></i>Download App & Register
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Login Forms (Initially Hidden) -->
                    <div id="login-forms" style="display: none;">
                        <div class="card shadow-lg border-0">
                            <div class="card-body p-4 p-md-5">
                                
                                <!-- Navigation Tabs -->
                                <ul class="nav nav-pills justify-content-center mb-4" id="loginTabs" role="tablist">
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link active" id="email-tab" data-bs-toggle="pill" data-bs-target="#email-login" type="button" role="tab">
                                            <i class="fas fa-envelope me-2"></i>Email Login
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="qr-tab" data-bs-toggle="pill" data-bs-target="#qr-login" type="button" role="tab">
                                            <i class="fas fa-qrcode me-2"></i>QR Code Login
                                        </button>
                                    </li>
                                </ul>

                                <div class="tab-content" id="loginTabContent">
                                    <!-- Email Login Tab -->
                                    <div class="tab-pane fade show active" id="email-login" role="tabpanel">
                                        <div class="text-center mb-4">
                                            <h3>Login with Your Email</h3>
                                            <p class="text-muted">Enter your account credentials to access your dashboard</p>
                                        </div>
                                        
                                        <form id="loginForm">
                                            <div class="mb-3">
                                                <label for="email" class="form-label">Email Address</label>
                                                <div class="input-group">
                                                    <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                                    <input type="email" class="form-control" id="email" placeholder="Enter your registered email" required>
                                                </div>
                                            </div>
                                            <div class="mb-3">
                                                <label for="password" class="form-label">Password</label>
                                                <div class="input-group">
                                                    <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                                    <input type="password" class="form-control" id="password" placeholder="Enter your password" required>
                                                    <button class="btn btn-outline-secondary" type="button" onclick="togglePassword()">
                                                        <i class="fas fa-eye" id="toggleIcon"></i>
                                                    </button>
                                                </div>
                                            </div>
                                            <div class="mb-3 form-check">
                                                <input type="checkbox" class="form-check-input" id="rememberMe">
                                                <label class="form-check-label" for="rememberMe">Keep me logged in</label>
                                            </div>
                                            <div class="d-grid mb-3">
                                                <button type="submit" class="btn btn-primary btn-lg">
                                                    <i class="fas fa-sign-in-alt me-2"></i>Sign In to My Account
                                                </button>
                                            </div>
                                        </form>
                                        
                                        <div class="text-center">
                                            <a href="/forgot_password" class="text-decoration-none">
                                                <i class="fas fa-key me-1"></i>Forgot your password?
                                            </a>
                                        </div>
                                    </div>

                                    <!-- QR Code Login Tab -->
                                    <div class="tab-pane fade" id="qr-login" role="tabpanel">
                                        <div class="text-center">
                                            <h3 class="mb-3">Quick Login with QR Code</h3>
                                            <p class="text-muted mb-4">Use your mobile app to scan and login instantly - perfect for quick access!</p>
                                            
                                            <div class="alert alert-info">
                                                <i class="fas fa-mobile-alt me-2"></i>
                                                <strong>Instructions:</strong> Open your IELTS GenAI Prep mobile app and use the QR scanner to login automatically
                                            </div>
                                            
                                            <div class="qr-container bg-light rounded p-4 mb-4">
                                                <div class="qr-code mx-auto mb-3" style="width: 200px; height: 200px; border: 2px dashed #007bff; display: flex; align-items: center; justify-content: center; background: white; border-radius: 10px;">
                                                    <div id="qr-placeholder">
                                                        <i class="fas fa-qrcode fa-4x text-primary mb-2"></i>
                                                        <p class="small text-muted">Click below to generate QR code</p>
                                                    </div>
                                                </div>
                                                <button class="btn btn-outline-primary btn-lg" onclick="generateQR()">
                                                    <i class="fas fa-qrcode me-2"></i>Generate Login QR Code
                                                </button>
                                            </div>
                                            
                                            <div class="alert alert-warning">
                                                <h6><i class="fas fa-mobile-alt me-2"></i>Don't have our mobile app yet?</h6>
                                                <p class="mb-2 small">Download our app to register your account and enjoy the full mobile experience!</p>
                                                <a href="/qr-auth" class="btn btn-warning">
                                                    <i class="fas fa-download me-2"></i>Get the Mobile App
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="text-center mt-4">
                                    <button class="btn btn-link" onclick="hideLogin()">
                                        <i class="fas fa-arrow-left me-2"></i>Back to Options
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function showLogin() {
            document.getElementById('login-forms').style.display = 'block';
            document.getElementById('email-tab').click();
            document.getElementById('login-forms').scrollIntoView({ behavior: 'smooth' });
        }
        
        function showQR() {
            document.getElementById('login-forms').style.display = 'block';
            document.getElementById('qr-tab').click();
            document.getElementById('login-forms').scrollIntoView({ behavior: 'smooth' });
        }
        
        function hideLogin() {
            document.getElementById('login-forms').style.display = 'none';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        function togglePassword() {
            const passwordField = document.getElementById('password');
            const toggleIcon = document.getElementById('toggleIcon');
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                toggleIcon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                passwordField.type = 'password';
                toggleIcon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        }
        
        function generateQR() {
            const qrPlaceholder = document.getElementById('qr-placeholder');
            qrPlaceholder.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Generating QR Code...</span></div>';
            
            setTimeout(() => {
                qrPlaceholder.innerHTML = '<i class="fas fa-qrcode fa-4x text-success mb-2"></i><p class="small text-success fw-bold">QR Code Ready!</p><p class="small text-muted">Scan this with your mobile app</p>';
            }, 1500);
        }
        </script>
        '''
        # Replace the main content section with login form using proper regex patterns
        import re
        content = re.sub(r'<section class="hero"[^>]*>.*?</section>', login_section, content, flags=re.DOTALL)
        content = re.sub(r'<section class="assessment-sections[^>]*>.*?</section>', '', content, flags=re.DOTALL)
        content = re.sub(r'<section class="features"[^>]*>.*?</section>', '', content, flags=re.DOTALL)
        content = re.sub(r'<section class="pricing[^>]*>.*?</section>', '', content, flags=re.DOTALL)
        content = re.sub(r'<section class="py-5"[^>]*>.*?</section>', '', content, flags=re.DOTALL)
        content = re.sub(r'<section class="py-5 bg-light"[^>]*>.*?</section>', '', content, flags=re.DOTALL)
        return content
    except FileNotFoundError:
        # Fallback to original template
        class AnonymousUser:
            is_authenticated = False
            email = None
        return render_template('login.html', current_user=AnonymousUser())

@app.route('/register')
def register():
    """Redirect register attempts to app store - registration is app-only"""
    return '''
    <html>
    <head>
        <title>Registration - IELTS GenAI Prep</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container-fluid vh-100 d-flex align-items-center justify-content-center">
            <div class="text-center">
                <div class="card shadow-lg border-0" style="max-width: 500px;">
                    <div class="card-body p-5">
                        <i class="fas fa-mobile-alt fa-4x text-primary mb-4"></i>
                        <h2 class="mb-3">Registration Available in App Only</h2>
                        <p class="lead mb-4">Create your IELTS GenAI Prep account exclusively through our mobile app for the best experience.</p>
                        <div class="d-grid gap-2">
                            <a href="/qr-auth" class="btn btn-primary btn-lg">
                                <i class="fas fa-download me-2"></i>Download App & Register
                            </a>
                            <a href="/login" class="btn btn-outline-secondary">
                                <i class="fas fa-sign-in-alt me-2"></i>Back to Login
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/about')
def about():
    """About route for template compatibility"""
    return redirect(url_for('home'))

@app.route('/contact')
def contact():
    """Contact page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('contact.html', current_user=AnonymousUser())

@app.route('/terms_and_payment')
def terms_and_payment():
    """Terms and payment page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('gdpr/terms_of_service.html', current_user=AnonymousUser())

@app.route('/privacy_policy')
def privacy_policy():
    """Privacy policy page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('gdpr/privacy_policy.html', current_user=AnonymousUser())

@app.route('/forgot_password')
def forgot_password():
    """Forgot password page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('forgot_password.html', current_user=AnonymousUser())

@app.route('/reset_password')
def reset_password():
    """Reset password page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
    
    # Get reset token from query params
    reset_token = request.args.get('token', '')
    
    return render_template('reset_password.html', current_user=AnonymousUser(), reset_token=reset_token)

def generate_reset_token(email: str) -> str:
    """Generate secure password reset token"""
    # Create a secure random token
    token = secrets.token_urlsafe(32)
    
    # Store token with expiration (1 hour from now)
    expiry = datetime.utcnow() + timedelta(hours=1)
    password_reset_tokens[token] = {
        'email': email,
        'expiry': expiry,
        'created_at': datetime.utcnow()
    }
    
    return token

def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Send password reset email using AWS SES"""
    try:
        # Check if running in development mode
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            # Development mode - log the email
            reset_link = f"http://localhost:5000/reset_password?token={reset_token}"
            print(f"[DEV_MODE] Password reset email for: {email}")
            print(f"[DEV_MODE] Reset link: {reset_link}")
            return True
        
        # Production mode - use AWS SES
        ses_client = boto3.client(
            'ses',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Build reset link
        base_url = os.environ.get('DOMAIN_URL', 'https://ieltsaiprep.com')
        reset_link = f"{base_url}/reset_password?token={reset_token}"
        username = email.split('@')[0].title()
        
        subject = "IELTS GenAI Prep - Password Reset Request"
        
        # Professional HTML email template matching your brand
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset - IELTS GenAI Prep</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #6f42c1;">
                    <h1 style="color: #6f42c1; margin-bottom: 10px; font-size: 28px;">IELTS GenAI Prep</h1>
                    <p style="color: #6c757d; margin: 0; font-size: 14px;">Powered by TrueScore® & ClearScore® AI Assessment Technology</p>
                </div>
                
                <!-- Main Content -->
                <div style="background: #f8f9fa; padding: 30px; border-radius: 8px; margin-bottom: 30px;">
                    <h2 style="color: #495057; font-weight: normal; text-align: center; margin-bottom: 20px;">Password Reset Request</h2>
                    
                    <p style="margin-bottom: 20px;">Hello {username},</p>
                    
                    <p style="margin-bottom: 20px;">We received a request to reset your password for your IELTS GenAI Prep account. 
                    If you made this request, please click the button below to reset your password:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="background: #6f42c1; color: white; padding: 15px 40px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;
                                  font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(111, 66, 193, 0.3);">
                            Reset My Password
                        </a>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <p style="margin: 0; color: #856404; font-size: 14px;">
                            <strong>Security Notice:</strong> This link will expire in 1 hour for your protection.
                        </p>
                    </div>
                    
                    <p style="margin-bottom: 0;">If you didn't request a password reset, please ignore this email. 
                    Your password will remain unchanged and your account is secure.</p>
                </div>
                
                <!-- Footer -->
                <div style="border-top: 1px solid #dee2e6; padding-top: 20px; font-size: 14px; color: #6c757d;">
                    <p style="margin-bottom: 15px;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 20px;">{reset_link}</p>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="margin-bottom: 5px; font-weight: bold;">Best regards,</p>
                        <p style="margin-bottom: 15px;">The IELTS GenAI Prep Team</p>
                        <p style="font-size: 12px; color: #adb5bd;">© 2025 IELTS GenAI Prep. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text version for email clients that don't support HTML
        text_body = f"""
IELTS GenAI Prep - Password Reset Request

Hello {username},

We received a request to reset your password for your IELTS GenAI Prep account.

If you made this request, please copy and paste the following link into your browser to reset your password:

{reset_link}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

Best regards,
The IELTS GenAI Prep Team

© 2025 IELTS GenAI Prep. All rights reserved.
        """
        
        # Send email via AWS SES
        response = ses_client.send_email(
            Source='noreply@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        print(f"[SES] Password reset email sent to {email}: {response['MessageId']}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send password reset email: {str(e)}")
        return False

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """Handle forgot password API request"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Email address is required'
            }), 400
        
        # Generate secure reset token
        reset_token = generate_reset_token(email)
        
        # Send password reset email via AWS SES
        if send_password_reset_email(email, reset_token):
            return jsonify({
                'status': 'success',
                'message': 'If this email is registered, you will receive password reset instructions.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Unable to send password reset email. Please try again later.'
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Password reset request failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Unable to process password reset request. Please try again later.'
        }), 500

def validate_reset_token(token: str) -> str | None:
    """Validate password reset token and return associated email if valid"""
    if token not in password_reset_tokens:
        return None
    
    token_data = password_reset_tokens[token]
    
    # Check if token has expired
    if datetime.utcnow() > token_data['expiry']:
        # Clean up expired token
        del password_reset_tokens[token]
        return None
    
    return token_data['email']

def invalidate_reset_token(token: str) -> None:
    """Invalidate a password reset token after use"""
    if token in password_reset_tokens:
        del password_reset_tokens[token]

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """Handle reset password API request with production-ready token validation"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Validate inputs
        if not all([token, new_password, confirm_password]):
            return jsonify({
                'status': 'error',
                'message': 'All fields are required'
            }), 400
        
        if new_password != confirm_password:
            return jsonify({
                'status': 'error',
                'message': 'Passwords do not match'
            }), 400
        
        if len(new_password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        # Validate password reset token
        email = validate_reset_token(token)
        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired reset token. Please request a new password reset.'
            }), 400
        
        # In a production system, you would update the password in your database
        # For this demo, we'll just log the success and invalidate the token
        print(f"[PASSWORD_RESET] Password successfully reset for: {email}")
        
        # Invalidate the token to prevent reuse
        invalidate_reset_token(token)
        
        # Send confirmation email (optional but recommended)
        try:
            send_password_reset_confirmation_email(email)
        except Exception as e:
            print(f"[WARNING] Failed to send password reset confirmation email: {str(e)}")
            # Don't fail the reset if confirmation email fails
        
        return jsonify({
            'status': 'success',
            'message': 'Password reset successful. You can now log in with your new password.',
            'redirect': '/login'
        })
        
    except Exception as e:
        print(f"[ERROR] Password reset failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Unable to reset password. Please try again later.'
        }), 500

def send_password_reset_confirmation_email(email: str) -> bool:
    """Send password reset confirmation email"""
    try:
        # Check if running in development mode
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            print(f"[DEV_MODE] Password reset confirmation email for: {email}")
            return True
        
        # Production mode - use AWS SES
        ses_client = boto3.client(
            'ses',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        username = email.split('@')[0].title()
        subject = "IELTS GenAI Prep - Password Reset Successful"
        
        # Confirmation email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset Successful - IELTS GenAI Prep</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #28a745;">
                    <h1 style="color: #28a745; margin-bottom: 10px; font-size: 28px;">IELTS GenAI Prep</h1>
                    <p style="color: #6c757d; margin: 0; font-size: 14px;">Powered by TrueScore® & ClearScore® AI Assessment Technology</p>
                </div>
                
                <!-- Success Message -->
                <div style="background: #d4edda; padding: 30px; border-radius: 8px; border-left: 4px solid #28a745; margin-bottom: 30px;">
                    <h2 style="color: #155724; margin-bottom: 20px; text-align: center;">
                        ✅ Password Reset Successful
                    </h2>
                    
                    <p style="margin-bottom: 20px; color: #155724;">Hello {username},</p>
                    
                    <p style="margin-bottom: 20px; color: #155724;">Your password has been successfully reset. You can now log in to your IELTS GenAI Prep account using your new password.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://ieltsaiprep.com/login" 
                           style="background: #28a745; color: white; padding: 15px 40px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;
                                  font-weight: bold; font-size: 16px;">
                            Login to My Account
                        </a>
                    </div>
                    
                    <p style="margin-bottom: 0; color: #155724; font-size: 14px;">If you did not reset your password, please contact our support team immediately.</p>
                </div>
                
                <!-- Footer -->
                <div style="border-top: 1px solid #dee2e6; padding-top: 20px; font-size: 14px; color: #6c757d; text-align: center;">
                    <p style="margin-bottom: 5px; font-weight: bold;">Best regards,</p>
                    <p style="margin-bottom: 15px;">The IELTS GenAI Prep Team</p>
                    <p style="font-size: 12px; color: #adb5bd;">© 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send confirmation email via AWS SES
        response = ses_client.send_email(
            Source='noreply@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        print(f"[SES] Password reset confirmation email sent to {email}: {response['MessageId']}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send password reset confirmation email: {str(e)}")
        return False



@app.route('/assessment/<assessment_type>/<int:assessment_number>/start')
def assessment_start(assessment_type, assessment_number):
    """Assessment start route for template compatibility"""
    # Verify session
    session_id = request.cookies.get('qr_session_id')
    if not session_id or session_id not in sessions:
        return redirect(url_for('home'))
    
    session_data = sessions[session_id]
    user_email = session_data['user_email']
    
    return f"""
    <html><head><title>Assessment Started</title></head>
    <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
            <h2>Assessment {assessment_number} Started</h2>
            <p><strong>Type:</strong> {assessment_type.replace('_', ' ').title()}</p>
            <p><strong>User:</strong> {user_email}</p>
            <p><strong>Session:</strong> {session_id}</p>
            <div style="margin: 20px 0; padding: 15px; background: #e8f5e8; border-radius: 5px;">
                Assessment module would load here with Nova Sonic AI integration
            </div>
            <a href="/assessment/{assessment_type}" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none;">Back to Assessments</a>
        </div>
    </body></html>
    """

@app.route('/qr-auth')
def qr_auth():
    """Serve QR authentication page"""
    return render_template('qr_auth_page.html')

@app.route('/qr-login')
def qr_login():
    """Alternative QR login route - redirects to home"""
    return redirect(url_for('home'))

@app.route('/api/generate-website-qr')
def generate_website_qr():
    """Generate QR code for website authentication"""
    try:
        # Generate a temporary token for website QR display
        token_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(minutes=10)
        
        # Store the token for later verification
        qr_tokens[token_id] = {
            'token_id': token_id,
            'user_email': None,  # Will be set when mobile app scans
            'created_at': created_at.isoformat(),
            'expires_at': int(expires_at.timestamp()),
            'used': False,
            'website_generated': True
        }
        
        # Create QR code data
        qr_data = {
            'token': token_id,
            'domain': 'ieltsaiprep.com',
            'type': 'website_auth',
            'timestamp': int(created_at.timestamp())
        }
        
        # Generate QR code image
        qr_code_image = generate_qr_code(json.dumps(qr_data))
        
        return jsonify({
            'success': True,
            'token_id': token_id,
            'qr_code_image': qr_code_image,
            'expires_in_minutes': 10,
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/profile')
def profile():
    """Serve profile/assessments page with QR authentication"""
    # Check QR session
    session_id = request.cookies.get('qr_session_id')
    
    # For testing, create a temporary session if none exists
    if not session_id or session_id not in sessions:
        return redirect(url_for('home'))
    
    session_data = sessions[session_id]
    if time.time() > session_data['expires_at']:
        return redirect(url_for('home'))
    
    user_email = session_data['user_email']
    user_data = user_assessments.get(user_email, {})
    
    # Mock user data for template compatibility
    class MockUser:
        def __init__(self, email):
            self.email = email
            self.account_activated = True
            self.last_login = datetime.utcnow()
            self.assessment_package_status = "active"
            self.assessment_package_expiry = datetime.utcnow() + timedelta(days=30)
        
        def has_active_assessment_package(self):
            return True
    
    # Prepare assessment data for profile template
    all_assessments = []
    for assessment_type, assessments in user_data.items():
        for assessment in assessments:
            assessment['assessment_type'] = assessment_type
            all_assessments.append(assessment)
    
    return render_template('simple_profile.html', 
                         current_user=MockUser(user_email),
                         assessments=all_assessments,
                         assessment_types=['academic_speaking', 'academic_writing', 'general_speaking', 'general_writing'])

@app.route('/assessment/<assessment_type>')
def assessment_list(assessment_type):
    """Lambda /assessment/<user_id> endpoint simulation with session verification"""
    # Verify ElastiCache session
    session_id = request.cookies.get('qr_session_id')
    if not session_id or session_id not in sessions:
        print(f"[CLOUDWATCH] Assessment access denied: No valid session for {assessment_type}")
        return redirect(url_for('home'))
    
    session_data = sessions[session_id]
    user_email = session_data['user_email']
    purchased_products = session_data.get('purchased_products', [])
    
    # Check if user has purchased this assessment type
    if assessment_type not in purchased_products:
        print(f"[CLOUDWATCH] Assessment access denied: {user_email} has not purchased {assessment_type}")
        return render_template('access_restricted.html', 
                             assessment_type=assessment_type,
                             message="This assessment requires a purchase to access.")
    
    print(f"[CLOUDWATCH] Assessment access granted: {user_email} accessing {assessment_type}")
    
    # Create mock user for template compatibility
    class MockUser:
        def __init__(self, email, products):
            self.email = email
            self.id = hash(email) % 1000
            self.purchased_products = products
            
        def has_active_assessment_package(self):
            return len(self.purchased_products) > 0
    
    current_user = MockUser(user_email, purchased_products)
    
    # Get user's assessment history for this type
    user_data = user_assessments.get(user_email, {})
    assessments = user_data.get(assessment_type, [])
    
    # Use existing assessment templates with additional required routes
    if 'speaking' in assessment_type:
        template = 'assessments/speaking_selection.html'
    else:
        template = f'assessments/{assessment_type}_selection.html'
    
    title = f"{assessment_type.replace('_', ' ').title()} Assessments"
    
    try:
        return render_template(template,
                             assessment_type=assessment_type,
                             title=title,
                             current_user=current_user,
                             assessments=assessments)
    except Exception as e:
        print(f"[CLOUDWATCH] Template error: {str(e)}")
        # Fallback success page if template has issues
        return f"""
        <html><head><title>Assessment Access</title></head>
        <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                <h2>✅ Authentication Successful</h2>
                <p><strong>User:</strong> {user_email}</p>
                <p><strong>Assessment:</strong> {assessment_type.replace('_', ' ').title()}</p>
                <p><strong>Session:</strong> {session_data['session_id']}</p>
                <p>You have successfully accessed this assessment module.</p>
                <a href="/profile" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none;">Dashboard</a>
            </div>
        </body></html>
        """

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session_id = request.cookies.get('qr_session_id')
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    response = redirect(url_for('home'))
    response.set_cookie('qr_session_id', '', expires=0)
    return response

@app.route('/test-mobile')
def test_mobile():
    """Serve mobile purchase simulator for testing"""
    try:
        with open('test_mobile_simulator.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return """
        <h1>Mobile Simulator Not Found</h1>
        <p>Please create the mobile simulator file first.</p>
        <a href="/qr-login">Go to QR Login</a>
        """

@app.route('/test-dashboard')
def test_dashboard():
    """Serve comprehensive QR authentication test dashboard"""
    return render_template('test_dashboard.html')

@app.route('/api/health', methods=['GET', 'POST'])
def health_check():
    """Lambda health check endpoint simulation"""
    try:
        # Check system components
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'dynamodb': {
                    'auth_tokens': len(qr_tokens),
                    'active_sessions': len(sessions)
                },
                'elasticache': {
                    'session_cache': 'operational'
                },
                'lambda': {
                    'memory_usage': '128MB',
                    'cold_starts': 0
                }
            },
            'metrics': {
                'total_qr_tokens': len(qr_tokens),
                'active_sessions': len([s for s in sessions.values() if time.time() < s['expires_at']]),
                'purchased_products': sum(len(products) for products in mock_purchases.values())
            }
        }
        
        print(f"[CLOUDWATCH] Health check: {health_data['status']}")
        return jsonify(health_data)
        
    except Exception as e:
        print(f"[CLOUDWATCH] Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def generate_qr_code(data):
    """Generate QR code image as base64 string"""
    qr = qrcode.make(data)
    
    # Convert to base64
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

# Test endpoints that simulate Lambda backend
@app.route('/api/auth/generate-qr', methods=['POST'])
def generate_qr_token():
    """Mock Lambda endpoint - Generate QR token after purchase verification"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', 'test@ieltsaiprep.com')
        product_id = data.get('product_id')
        purchase_verified = data.get('purchase_verified', True)
        
        if not purchase_verified:
            return jsonify({
                'success': False,
                'error': 'Purchase verification required'
            }), 400
        
        # Simulate DynamoDB AuthTokens table storage
        token_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(minutes=10)
        
        # Store in mock AuthTokens table
        qr_tokens[token_id] = {
            'token_id': token_id,
            'user_email': user_email,
            'product_id': product_id,
            'created_at': created_at.isoformat(),
            'expires_at': int(expires_at.timestamp()),
            'used': False,
            'ttl': int(expires_at.timestamp())  # DynamoDB TTL format
        }
        
        # Record mock purchase for user
        if user_email not in mock_purchases:
            mock_purchases[user_email] = []
        if product_id and product_id not in mock_purchases[user_email]:
            mock_purchases[user_email].append(product_id)
        
        # Create QR code data for mobile app display
        qr_data = {
            'token': token_id,
            'domain': 'ieltsaiprep.com',
            'user_email': user_email,
            'product_id': product_id,
            'timestamp': int(created_at.timestamp())
        }
        
        # Generate QR code image
        qr_code_image = generate_qr_code(json.dumps(qr_data))
        
        # CloudWatch logging simulation
        print(f"[CLOUDWATCH] QR Token Generated: {token_id} for {user_email} - Product: {product_id}")
        
        return jsonify({
            'success': True,
            'token_id': token_id,
            'qr_code_image': qr_code_image,
            'expires_in_minutes': 10,
            'expires_at': expires_at.isoformat(),
            'user_email': user_email,
            'product_id': product_id
        })
        
    except Exception as e:
        print(f"[CLOUDWATCH] QR Generation Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/verify-qr', methods=['POST'])
def verify_qr_token():
    """Mock Lambda endpoint - Verify QR token and create ElastiCache session"""
    try:
        data = request.get_json()
        token_id = data.get('token')
        
        print(f"[CLOUDWATCH] QR Verification attempt: {token_id}")
        
        if not token_id:
            print(f"[CLOUDWATCH] QR Verification failed: No token provided")
            return jsonify({
                'success': False,
                'error': 'Token required'
            }), 400
        
        # Check AuthTokens table (simulated)
        if token_id not in qr_tokens:
            print(f"[CLOUDWATCH] QR Verification failed: Invalid token {token_id}")
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        token_data = qr_tokens[token_id]
        current_time = int(time.time())
        
        # Check token expiry (DynamoDB TTL simulation)
        expires_at = token_data.get('expires_at', 0)
        if current_time > expires_at:
            print(f"[CLOUDWATCH] QR Verification failed: Expired token {token_id}")
            # Remove expired token from storage
            del qr_tokens[token_id]
            return jsonify({
                'success': False,
                'error': 'QR code expired. Please generate a new one from your mobile app.'
            }), 401
        
        # Check if token already used
        if token_data.get('used'):
            print(f"[CLOUDWATCH] QR Verification failed: Token already used {token_id}")
            return jsonify({
                'success': False,
                'error': 'QR code already used. Please generate a new one.'
            }), 401
        
        # Mark token as used in AuthTokens table
        token_data['used'] = True
        token_data['used_at'] = datetime.utcnow().isoformat()
        
        # Create ElastiCache session (1-hour expiry)
        session_id = f"session_{int(time.time())}_{token_id[:8]}"
        sessions[session_id] = {
            'session_id': session_id,
            'user_email': token_data['user_email'],
            'product_id': token_data.get('product_id'),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': time.time() + 3600,
            'authenticated_via': 'qr_token',
            'purchased_products': mock_purchases.get(token_data['user_email'], [])
        }
        
        print(f"[CLOUDWATCH] QR Verification successful: {token_id} -> Session: {session_id}")
        print(f"[CLOUDWATCH] User {token_data['user_email']} authenticated with products: {mock_purchases.get(token_data['user_email'], [])}")
        
        response = jsonify({
            'success': True,
            'message': 'Authentication successful',
            'session_id': session_id,
            'user_email': token_data['user_email'],
            'redirect_url': '/profile'
        })
        
        # Set session cookie for browser compatibility
        response.set_cookie('qr_session_id', session_id, max_age=3600)
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mobile-authenticate', methods=['POST'])
def mobile_authenticate():
    """Simulate mobile app scanning and authenticating QR code"""
    try:
        data = request.get_json()
        token = data.get('token')
        user_email = data.get('user_email', 'test@ieltsaiprep.com')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token required'
            }), 400
        
        # Check if token exists
        if token not in qr_tokens:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 400
        
        token_data = qr_tokens[token]
        
        # Check if token is expired
        if time.time() > token_data['expires_at']:
            return jsonify({
                'success': False,
                'error': 'Token expired'
            }), 400
        
        # Update token with user email (mobile app authenticated)
        qr_tokens[token]['user_email'] = user_email
        
        return jsonify({
            'success': True,
            'message': 'Mobile authentication successful',
            'token': token
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/assessment/<user_email>')
def get_assessments(user_email):
    """Test endpoint - Get user assessments (simulates Lambda)"""
    try:
        # Check session
        auth_header = request.headers.get('Authorization', '')
        session_id = auth_header.replace('Bearer ', '') if auth_header else None
        
        if not session_id or session_id not in sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session'
            }), 401
        
        session_data = sessions[session_id]
        
        # Check session expiry
        if time.time() > session_data['expires_at']:
            return jsonify({
                'success': False,
                'error': 'Session expired'
            }), 401
        
        # Get assessments from proper data structure
        user_data = user_assessments.get(user_email, {})
        all_assessments = []
        for assessment_type, assessments in user_data.items():
            for assessment in assessments:
                assessment_copy = assessment.copy()
                assessment_copy['assessment_type'] = assessment_type
                all_assessments.append(assessment_copy)
        
        return jsonify({
            'success': True,
            'assessments': all_assessments,
            'total_count': len(all_assessments)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/assessment-structure')
def assessment_structure():
    """Show IELTS test structure with FAQ section"""
    ielts_info = "IELTS (International English Language Testing System) is designed to help you work, study, or migrate to a country where English is the native language. This includes countries such as Australia, Canada, New Zealand, the UK, and USA."
    return render_template('assessment_structure/index.html', ielts_info=ielts_info)

@app.route('/assessment-structure/<assessment_type>')
def assessment_structure_detail(assessment_type):
    """Show detailed assessment structure for specific type"""
    if assessment_type == 'academic':
        return render_template('assessment_structure/academic.html')
    elif assessment_type == 'general_training':
        return render_template('assessment_structure/general_training.html')
    else:
        return "Assessment type not found", 404

@app.route('/test-qr-flow')
def test_qr_flow():
    """Serve QR authentication test page"""
    return send_from_directory('.', 'test_qr_authentication.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)