"""
Cloud Function for App Store and Google Play Receipt Validation
Handles in-app purchase verification
"""
import functions_framework
import json
import logging
import os
import requests
from typing import Dict, Any
from google.cloud import firestore
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize Firestore
db = firestore.Client()

@functions_framework.http
def validate_receipt(request):
    """
    HTTP Cloud Function for receipt validation
    
    Args:
        request: Flask Request object with JSON:
            {
                "platform": "apple" | "google",
                "receipt_data": <base64 or token>,
                "user_id": <string>,
                "product_id": <string>
            }
    
    Returns:
        JSON response with validation result
    """
    # CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({'error': 'Invalid request'}), 400, headers)
        
        platform = request_json.get('platform')
        receipt_data = request_json.get('receipt_data')
        user_id = request_json.get('user_id')
        product_id = request_json.get('product_id')
        
        if not all([platform, receipt_data, user_id, product_id]):
            return (json.dumps({'error': 'Missing required fields'}), 400, headers)
        
        # Validate receipt
        if platform == 'apple':
            result = validate_apple_receipt(receipt_data, product_id)
        elif platform == 'google':
            result = validate_google_receipt(receipt_data, product_id)
        else:
            return (json.dumps({'error': 'Invalid platform'}), 400, headers)
        
        if result['valid']:
            # Store entitlement in Firestore
            entitlement_id = store_entitlement(
                user_id, 
                product_id, 
                platform, 
                result['receipt_info']
            )
            
            return (json.dumps({
                'valid': True,
                'entitlement_id': entitlement_id,
                'product_id': product_id
            }), 200, headers)
        else:
            return (json.dumps({
                'valid': False,
                'error': result.get('error', 'Invalid receipt')
            }), 400, headers)
    
    except Exception as e:
        logger.error(f"Receipt validation error: {e}")
        return (json.dumps({'error': str(e)}), 500, headers)


def validate_apple_receipt(receipt_data: str, product_id: str) -> Dict[str, Any]:
    """Validate Apple App Store receipt"""
    try:
        shared_secret = os.environ.get('APPLE_SHARED_SECRET')
        
        # Try production first, then sandbox
        for url in [
            'https://buy.itunes.apple.com/verifyReceipt',
            'https://sandbox.itunes.apple.com/verifyReceipt'
        ]:
            response = requests.post(
                url,
                json={
                    'receipt-data': receipt_data,
                    'password': shared_secret,
                    'exclude-old-transactions': True
                },
                timeout=10
            )
            
            result = response.json()
            status = result.get('status')
            
            # 0 = valid, 21007 = sandbox receipt sent to production
            if status == 0:
                # Check if product matches
                latest_receipt_info = result.get('latest_receipt_info', [])
                for receipt in latest_receipt_info:
                    if receipt.get('product_id') == product_id:
                        return {
                            'valid': True,
                            'receipt_info': receipt
                        }
            elif status == 21007:
                # Try sandbox
                continue
            else:
                break
        
        return {'valid': False, 'error': f'Apple validation failed: {status}'}
        
    except Exception as e:
        logger.error(f"Apple receipt validation error: {e}")
        return {'valid': False, 'error': str(e)}


def validate_google_receipt(purchase_token: str, product_id: str) -> Dict[str, Any]:
    """Validate Google Play purchase"""
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        # Get service account credentials
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(service_account_json),
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )
        credentials.refresh(Request())
        
        # Call Google Play Developer API
        package_name = os.environ.get('ANDROID_PACKAGE_NAME', 'com.ieltsaiprep.app')
        url = f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/purchases/products/{product_id}/tokens/{purchase_token}'
        
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {credentials.token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            purchase_data = response.json()
            
            # Check if purchase is valid (purchaseState == 0)
            if purchase_data.get('purchaseState') == 0:
                return {
                    'valid': True,
                    'receipt_info': purchase_data
                }
        
        return {'valid': False, 'error': 'Google validation failed'}
        
    except Exception as e:
        logger.error(f"Google receipt validation error: {e}")
        return {'valid': False, 'error': str(e)}


def store_entitlement(user_id: str, product_id: str, platform: str, receipt_info: Dict) -> str:
    """Store validated entitlement in Firestore with assessment count"""
    import secrets
    
    # Product assessment count mapping (2 assessments per purchase)
    product_assessments = {
        'com.ieltsaiprep.academic.writing': 2,
        'com.ieltsaiprep.general.writing': 2,
        'com.ieltsaiprep.academic.speaking': 2,
        'com.ieltsaiprep.general.speaking': 2,
        'com.ieltsaiprep.academic.mocktest': 2,
        'com.ieltsaiprep.general.mocktest': 2,
        # Legacy product IDs
        'academic_writing': 2,
        'general_writing': 2,
        'academic_speaking': 2,
        'general_speaking': 2,
    }
    
    entitlement_id = f"ent_{secrets.token_urlsafe(16)}"
    assessments_count = product_assessments.get(product_id, 2)
    
    entitlement_data = {
        'entitlement_id': entitlement_id,
        'user_id': user_id,
        'product_id': product_id,
        'platform': platform,
        'receipt_data': receipt_info,
        'status': 'active',
        'assessments_total': assessments_count,
        'assessments_remaining': assessments_count,
        'assessments_used': 0,
        'created_at': datetime.utcnow(),
        'consumed': False
    }
    
    db.collection('entitlements').document(entitlement_id).set(entitlement_data)
    
    return entitlement_id
