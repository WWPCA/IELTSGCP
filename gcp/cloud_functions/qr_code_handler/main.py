"""
Cloud Function for QR Code Generation and Validation
Handles QR code authentication for mobile-to-web transitions
"""
import functions_framework
import json
import logging
import secrets
import qrcode
import io
import base64
from google.cloud import firestore
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Firestore
db = firestore.Client()

@functions_framework.http
def handle_qr_code(request):
    """
    HTTP Cloud Function for QR code operations
    
    POST /generate - Generate QR code for user
    POST /validate - Validate QR code token
    """
    # CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({'error': 'Invalid request'}), 400, headers)
        
        action = request.path.split('/')[-1]  # 'generate' or 'validate'
        
        if action == 'generate':
            return generate_qr_code(request_json, headers)
        elif action == 'validate':
            return validate_qr_code(request_json, headers)
        else:
            return (json.dumps({'error': 'Invalid action'}), 400, headers)
    
    except Exception as e:
        logger.error(f"QR code handler error: {e}")
        return (json.dumps({'error': str(e)}), 500, headers)


def generate_qr_code(request_data: dict, headers: dict):
    """Generate QR code for user"""
    user_id = request_data.get('user_id')
    device_info = request_data.get('device_info', {})
    
    if not user_id:
        return (json.dumps({'error': 'Missing user_id'}), 400, headers)
    
    # Generate unique token
    token = secrets.token_urlsafe(32)
    
    # Store in Firestore with 5-minute expiration
    qr_data = {
        'token': token,
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(minutes=5),
        'used': False,
        'device_info': device_info
    }
    
    db.collection('qr_tokens').document(token).set(qr_data)
    
    # Generate QR code image
    qr_url = f"https://www.ieltsaiprep.com/qr-login?token={token}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    
    return (json.dumps({
        'token': token,
        'qr_image': f'data:image/png;base64,{img_base64}',
        'qr_url': qr_url,
        'expires_in': 300  # 5 minutes
    }), 200, headers)


def validate_qr_code(request_data: dict, headers: dict):
    """Validate QR code token"""
    token = request_data.get('token')
    
    if not token:
        return (json.dumps({'error': 'Missing token'}), 400, headers)
    
    try:
        # Get token from Firestore
        doc_ref = db.collection('qr_tokens').document(token)
        doc = doc_ref.get()
        
        if not doc.exists:
            return (json.dumps({'valid': False, 'error': 'Invalid token'}), 400, headers)
        
        qr_data = doc.to_dict()
        
        # Check if already used
        if qr_data.get('used'):
            return (json.dumps({'valid': False, 'error': 'Token already used'}), 400, headers)
        
        # Check expiration
        if qr_data.get('expires_at') < datetime.utcnow():
            return (json.dumps({'valid': False, 'error': 'Token expired'}), 400, headers)
        
        # Mark as used
        doc_ref.update({'used': True, 'used_at': datetime.utcnow()})
        
        return (json.dumps({
            'valid': True,
            'user_id': qr_data['user_id']
        }), 200, headers)
        
    except Exception as e:
        logger.error(f"QR validation error: {e}")
        return (json.dumps({'valid': False, 'error': str(e)}), 500, headers)
