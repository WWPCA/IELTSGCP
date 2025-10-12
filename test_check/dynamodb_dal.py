"""
AWS DynamoDB Data Access Layer for IELTS AI Prep
Replaces Firestore with real AWS DynamoDB integration
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import secrets
import json
import os
import logging

logger = logging.getLogger(__name__)

# Product configuration - number of assessments per purchase
PRODUCT_ASSESSMENTS = {
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

class DynamoDBConnection:
    """Manages DynamoDB connection for AWS"""
    
    def __init__(self, region: str = None, environment: str = None):
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.environment = environment or os.environ.get('ENVIRONMENT', 'production')
        
        # Initialize DynamoDB resource
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=self.region,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Table name mapping
        self.table_names = {
            'users': 'ielts-genai-prep-users',
            'sessions': 'ielts-genai-prep-sessions',
            'assessments': 'ielts-genai-prep-assessments',
            'qr_tokens': 'ielts-genai-prep-qr-tokens',
            'entitlements': 'ielts-genai-prep-entitlements',
            'questions': 'ielts-assessment-questions',
            'rubrics': 'ielts-assessment-rubrics',
            'ai_safety_logs': 'ielts-ai-safety-logs',
            'content_reports': 'ielts-content-reports'
        }
        
        logger.info(f"DynamoDB client initialized - region: {self.region}, environment: {self.environment}")
    
    def get_table(self, table_key: str):
        """Get DynamoDB table reference"""
        table_name = self.table_names.get(table_key)
        if not table_name:
            raise ValueError(f"Unknown table key: {table_key}")
        return self.dynamodb.Table(table_name)

class UserDAL:
    """User Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('users')
    
    def create_user(self, email: str, password: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Create new user account"""
        try:
            # Check if user already exists
            existing = self.get_user_by_email(email)
            if existing:
                logger.warning(f"User already exists: {email}")
                return None
            
            user_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            user_data = {
                'email': email,
                'user_id': user_id,
                'password_hash': generate_password_hash(password),
                'created_at': now.isoformat(),
                'last_login': now.isoformat(),
                'join_date': now.isoformat(),
                'email_verified': kwargs.get('email_verified', False),
                'assessment_count': 0,
                'is_active': True,
                **kwargs
            }
            
            # Remove password if passed in kwargs
            user_data.pop('password', None)
            
            self.table.put_item(Item=user_data)
            logger.info(f"User created: {email}")
            
            # Remove sensitive data before returning
            user_data.pop('password_hash', None)
            return user_data
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            response = self.table.get_item(Key={'email': email})
            user = response.get('Item')
            if user:
                logger.info(f"User found: {email}")
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def verify_password(self, email: str, password: str) -> bool:
        """Verify user password"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return False
            
            password_hash = user.get('password_hash')
            if not password_hash:
                return False
                
            return check_password_hash(password_hash, password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def update_user(self, email: str, **updates) -> bool:
        """Update user data"""
        try:
            if not updates:
                return True
            
            update_expr_parts = []
            expr_values = {}
            expr_names = {}
            
            for key, value in updates.items():
                # Handle reserved keywords
                attr_name = f"#{key}"
                attr_value = f":{key}"
                update_expr_parts.append(f"{attr_name} = {attr_value}")
                expr_names[attr_name] = key
                expr_values[attr_value] = value
            
            update_expr = "SET " + ", ".join(update_expr_parts)
            
            self.table.update_item(
                Key={'email': email},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values
            )
            
            logger.info(f"User updated: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def update_last_login(self, email: str) -> bool:
        """Update user's last login timestamp"""
        return self.update_user(email, last_login=datetime.utcnow().isoformat())
    
    def get_sanitized_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from user object"""
        if not user_data:
            return None
        
        sanitized = user_data.copy()
        sanitized.pop('password_hash', None)
        sanitized.pop('reset_token', None)
        sanitized.pop('reset_token_expires', None)
        
        return sanitized

class SessionDAL:
    """Session Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('sessions')
    
    def create_session(self, user_email: str, user_id: str, session_type: str = 'web') -> Dict[str, Any]:
        """Create new session"""
        try:
            session_id = f"{session_type}_{int(datetime.utcnow().timestamp())}_{str(uuid.uuid4())[:8]}"
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=24)
            
            session_data = {
                'session_id': session_id,
                'user_email': user_email,
                'user_id': user_id,
                'created_at': now.isoformat(),
                'expires_at': int(expires_at.timestamp()),  # TTL in Unix timestamp
                'session_type': session_type,
                'is_active': True
            }
            
            self.table.put_item(Item=session_data)
            logger.info(f"Session created: {session_id} for {user_email}")
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            session = response.get('Item')
            
            if session:
                # Check if expired
                if session.get('expires_at', 0) < datetime.utcnow().timestamp():
                    logger.info(f"Session expired: {session_id}")
                    return None
                    
            return session
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session (logout)"""
        try:
            self.table.delete_item(Key={'session_id': session_id})
            logger.info(f"Session deleted: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

class AssessmentDAL:
    """Assessment Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('assessments')
    
    def save_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save assessment result"""
        try:
            if 'assessment_id' not in assessment_data:
                assessment_data['assessment_id'] = str(uuid.uuid4())
            
            if 'timestamp' not in assessment_data:
                assessment_data['timestamp'] = datetime.utcnow().isoformat()
            
            self.table.put_item(Item=assessment_data)
            logger.info(f"Assessment saved: {assessment_data['assessment_id']}")
            
            return assessment_data
            
        except Exception as e:
            logger.error(f"Error saving assessment: {e}")
            return None
    
    def get_user_assessments(self, user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's assessment history"""
        try:
            # Query using GSI on user_email
            response = self.table.query(
                IndexName='user-email-index',
                KeyConditionExpression=Key('user_email').eq(user_email),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error getting assessments: {e}")
            return []
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get specific assessment by ID"""
        try:
            response = self.table.get_item(Key={'assessment_id': assessment_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Error getting assessment: {e}")
            return None

class QRTokenDAL:
    """QR Token Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('qr_tokens')
    
    def create_token(self, user_email: str, purpose: str = 'auth') -> Dict[str, Any]:
        """Create QR authentication token"""
        try:
            token = secrets.token_urlsafe(32)
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=5)
            
            token_data = {
                'token': token,
                'user_email': user_email,
                'purpose': purpose,
                'created_at': now.isoformat(),
                'expires_at': int(expires_at.timestamp()),  # TTL
                'used': False
            }
            
            self.table.put_item(Item=token_data)
            logger.info(f"QR token created for {user_email}")
            
            return token_data
            
        except Exception as e:
            logger.error(f"Error creating QR token: {e}")
            return None
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and consume QR token"""
        try:
            response = self.table.get_item(Key={'token': token})
            token_data = response.get('Item')
            
            if not token_data:
                return None
            
            # Check expiry
            if token_data.get('expires_at', 0) < datetime.utcnow().timestamp():
                logger.info(f"QR token expired: {token}")
                return None
            
            # Check if already used
            if token_data.get('used'):
                logger.info(f"QR token already used: {token}")
                return None
            
            # Mark as used
            self.table.update_item(
                Key={'token': token},
                UpdateExpression="SET used = :used",
                ExpressionAttributeValues={':used': True}
            )
            
            return token_data
            
        except Exception as e:
            logger.error(f"Error validating QR token: {e}")
            return None

# Compatibility aliases for easy migration from Firestore
FirestoreConnection = DynamoDBConnection  # Alias for compatibility