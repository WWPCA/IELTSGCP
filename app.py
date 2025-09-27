"""
QR Authentication Test Server for .replit environment
Serves frontend and provides local test endpoints that simulate Lambda backend
"""

from flask import Flask, send_from_directory, render_template, request, jsonify, redirect, url_for

# Mock functions for template compatibility
def csrf_token():
    return "mock-csrf-token"

class MockConfig:
    RECAPTCHA_SITE_KEY = "mock-recaptcha-key"

app = Flask(__name__)
app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = MockConfig()
app.secret_key = 'dev-secret-key-for-testing'
import json
import uuid
import time
import qrcode
import io
import base64
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = MockConfig()

# In-memory storage for testing (simulates DynamoDB and ElastiCache)
qr_tokens = {}  # Simulates AuthTokens DynamoDB table
sessions = {}   # Simulates ElastiCache session storage
mock_purchases = {}  # Simulates user purchase records
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
    """Serve working template with comprehensive FAQ and all features"""
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        # Fallback to index.html if working template not found
        class AnonymousUser:
            is_authenticated = False
            email = None
        return render_template('index.html', current_user=AnonymousUser())

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

@app.route('/login')
def login():
    """Login page - maintain consistency with working template design"""
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        # Inject enhanced mobile-first login form with QR code option
        login_section = '''
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-12 col-md-10 col-lg-8">
                    <div class="card shadow-lg border-0">
                        <div class="card-body p-4 p-md-5">
                            <h2 class="text-center mb-4 fw-bold">Login to IELTS GenAI Prep</h2>
                            
                            <!-- Mobile-First Tab Navigation -->
                            <ul class="nav nav-pills justify-content-center mb-4" id="loginTabs" role="tablist">
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active" id="email-tab" data-bs-toggle="pill" data-bs-target="#email-login" type="button" role="tab">
                                        <i class="fas fa-envelope me-2"></i>Email Login
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="qr-tab" data-bs-toggle="pill" data-bs-target="#qr-login" type="button" role="tab">
                                        <i class="fas fa-qrcode me-2"></i>QR Code
                                    </button>
                                </li>
                            </ul>

                            <div class="tab-content" id="loginTabContent">
                                <!-- Email Login Tab -->
                                <div class="tab-pane fade show active" id="email-login" role="tabpanel">
                                    <form id="loginForm">
                                        <div class="mb-3">
                                            <label for="email" class="form-label">Email Address</label>
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                                <input type="email" class="form-control" id="email" placeholder="Enter your email" required>
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
                                            <label class="form-check-label" for="rememberMe">Remember me on this device</label>
                                        </div>
                                        <div class="d-grid mb-3">
                                            <button type="submit" class="btn btn-primary btn-lg">
                                                <i class="fas fa-sign-in-alt me-2"></i>Login
                                            </button>
                                        </div>
                                        
                                        <!-- Mobile Purchase Option -->
                                        <div class="text-center mb-3">
                                            <div class="alert alert-info">
                                                <i class="fas fa-mobile-alt me-2"></i>
                                                <strong>Mobile Users:</strong> Prefer purchasing assessments directly through our mobile app for the best experience!
                                            </div>
                                            <a href="/qr-auth" class="btn btn-success btn-lg w-100 mb-2">
                                                <i class="fas fa-shopping-cart me-2"></i>Purchase via Mobile App
                                            </a>
                                        </div>
                                    </form>
                                </div>

                                <!-- QR Code Login Tab -->
                                <div class="tab-pane fade" id="qr-login" role="tabpanel">
                                    <div class="text-center">
                                        <h4 class="mb-3">Quick Mobile Login</h4>
                                        <p class="text-muted mb-4">Scan this QR code with your IELTS GenAI mobile app to login instantly</p>
                                        
                                        <div class="qr-container bg-light rounded p-4 mb-4">
                                            <div class="qr-code mx-auto mb-3" style="width: 200px; height: 200px; border: 2px dashed #007bff; display: flex; align-items: center; justify-content: center; background: white; border-radius: 10px;">
                                                <div id="qr-placeholder">
                                                    <i class="fas fa-qrcode fa-4x text-primary mb-2"></i>
                                                    <p class="small text-muted">QR Code will appear here</p>
                                                </div>
                                            </div>
                                            <button class="btn btn-outline-primary" onclick="generateQR()">
                                                <i class="fas fa-refresh me-2"></i>Generate QR Code
                                            </button>
                                        </div>
                                        
                                        <div class="alert alert-warning">
                                            <h6><i class="fas fa-mobile-alt me-2"></i>Don't have the mobile app?</h6>
                                            <a href="/qr-auth" class="btn btn-warning btn-sm">
                                                <i class="fas fa-download me-2"></i>Download App & Purchase
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <hr class="my-4">
                            <div class="text-center">
                                <p class="mb-2"><a href="/forgot_password" class="text-decoration-none">
                                    <i class="fas fa-key me-1"></i>Forgot your password?
                                </a></p>
                                <p class="mb-0">Don't have an account? <a href="/register" class="fw-bold text-decoration-none">
                                    <i class="fas fa-user-plus me-1"></i>Sign up here
                                </a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
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
            qrPlaceholder.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Generating...</span></div>';
            
            // Simulate QR generation
            setTimeout(() => {
                qrPlaceholder.innerHTML = '<i class="fas fa-qrcode fa-4x text-success mb-2"></i><p class="small text-success">QR Code Generated!</p><p class="small text-muted">Scan with your mobile app</p>';
            }, 2000);
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
    """Register page - maintain consistency with working template design"""
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        # Inject register form into the working template
        register_section = '''
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-8 col-lg-6">
                    <div class="card shadow-lg">
                        <div class="card-body p-5">
                            <h2 class="text-center mb-4">Join IELTS GenAI Prep</h2>
                            <form id="registerForm">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="firstName" class="form-label">First Name</label>
                                        <input type="text" class="form-control" id="firstName" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="lastName" class="form-label">Last Name</label>
                                        <input type="text" class="form-control" id="lastName" required>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email</label>
                                    <input type="email" class="form-control" id="email" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" required>
                                </div>
                                <div class="mb-3">
                                    <label for="confirmPassword" class="form-label">Confirm Password</label>
                                    <input type="password" class="form-control" id="confirmPassword" required>
                                </div>
                                <div class="mb-3 form-check">
                                    <input type="checkbox" class="form-check-input" id="agreeTerms" required>
                                    <label class="form-check-label" for="agreeTerms">I agree to the Terms of Service and Privacy Policy</label>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-success btn-lg">Create Account</button>
                                </div>
                            </form>
                            <hr>
                            <div class="text-center">
                                <p>Already have an account? <a href="/login">Sign in here</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        # Replace the main content section with register form using proper regex patterns
        import re
        content = re.sub(r'<section class="hero"[^>]*>.*?</section>', register_section, content, flags=re.DOTALL)
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
        return render_template('register.html', current_user=AnonymousUser())

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
        
        # Mock password reset for development
        print(f"[MOCK_EMAIL] Password reset requested for: {email}")
        print(f"[MOCK_EMAIL] Reset link: http://localhost:5000/reset_password?token=mock-token-{email}")
        
        return jsonify({
            'status': 'success',
            'message': 'If this email is registered, you will receive password reset instructions.'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Unable to process password reset request. Please try again later.'
        }), 500

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """Handle reset password API request"""
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
        
        # Mock password reset success for development
        print(f"[MOCK_RESET] Password reset successful for token: {token}")
        
        return jsonify({
            'status': 'success',
            'message': 'Password reset successful. You can now log in with your new password.',
            'redirect': '/login'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Unable to reset password. Please try again later.'
        }), 500



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