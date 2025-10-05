"""
Firestore Data Access Layer for IELTS GenAI Prep
Replaces DynamoDB with Google Cloud Firestore for multi-region deployment
"""
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging
import secrets
import os

logger = logging.getLogger(__name__)


class FirestoreConnection:
    """Manages Firestore connection with multi-region support"""
    
    def __init__(self, project_id: Optional[str] = None, environment: Optional[str] = None):
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.environment = environment or os.environ.get('ENVIRONMENT', 'production')
        
        # Firestore automatically handles multi-region replication with nam5/eur3
        self.db = firestore.Client(project=self.project_id)
        self.regions = ['us-central1', 'europe-west1', 'asia-southeast1']
        
        # Use environment prefix for collection isolation
        self.collection_prefix = f"{self.environment}_" if self.environment != 'production' else ""
        
        logger.info(f"Firestore client initialized - project: {self.project_id}, environment: {self.environment}, prefix: {self.collection_prefix}")
    
    def get_collection(self, collection_name: str) -> firestore.CollectionReference:
        """Get Firestore collection reference with environment prefix"""
        prefixed_name = f"{self.collection_prefix}{collection_name}"
        return self.db.collection(prefixed_name)


class UserDAL:
    """User Data Access Layer using Firestore"""
    
    def __init__(self, connection: FirestoreConnection):
        self.conn = connection
        self.collection = connection.get_collection('users')
        # Create composite indexes for common queries
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure Firestore indexes exist (configured in firestore.indexes.json)"""
        # Indexes: email, username, user_id for lookups
        pass
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = None, **kwargs) -> Dict[str, Any]:
        """Create a new user"""
        user_id = self._generate_user_id()
        password_hash = generate_password_hash(password)
        
        now = datetime.utcnow()
        user_data = {
            'email': email.lower(),
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'full_name': full_name,
            'profile_picture': None,
            'bio': None,
            'join_date': now,
            'last_login': None,
            'created_at': now,
            'reset_token': None,
            'reset_token_expires': None,
            'is_active': True,
            'assessment_package_status': 'none',
            'assessment_package_expiry': None,
            'subscription_status': 'none',
            'subscription_expiry': None,
            'preferred_language': 'en',
            'preferences': {}
        }
        
        try:
            # Check if email exists
            if self.get_user_by_email(email):
                raise ValueError("Email already exists")
            
            # Check if username exists
            if self.get_user_by_username(username):
                raise ValueError("Username already exists")
            
            # Use email as document ID for efficient lookups
            doc_ref = self.collection.document(email.lower())
            doc_ref.set(user_data)
            
            return self._format_user_response(user_data)
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user_id"""
        try:
            # Query by user_id field
            users = self.collection.where(
                filter=FieldFilter('user_id', '==', user_id)
            ).limit(1).stream()
            
            for user in users:
                return self._format_user_response(user.to_dict())
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email - direct document lookup"""
        try:
            doc_ref = self.collection.document(email.lower())
            doc = doc_ref.get()
            
            if doc.exists:
                return self._format_user_response(doc.to_dict())
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            users = self.collection.where(
                filter=FieldFilter('username', '==', username)
            ).limit(1).stream()
            
            for user in users:
                return self._format_user_response(user.to_dict())
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            return None
    
    def update_user(self, email: str, **updates) -> bool:
        """Update user fields"""
        try:
            doc_ref = self.collection.document(email.lower())
            
            # Remove None values
            updates = {k: v for k, v in updates.items() if v is not None}
            updates['updated_at'] = datetime.utcnow()
            
            doc_ref.update(updates)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user {email}: {e}")
            return False
    
    def delete_user(self, email: str) -> bool:
        """Delete user"""
        try:
            self.collection.document(email.lower()).delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {email}: {e}")
            return False
    
    def verify_password(self, email: str, password: str) -> bool:
        """Verify user password"""
        user = self.get_user_by_email(email)
        if user and user.get('password_hash'):
            return check_password_hash(user['password_hash'], password)
        return False
    
    def update_last_login(self, email: str):
        """Update user last login timestamp"""
        return self.update_user(email, last_login=datetime.utcnow())
    
    def set_reset_token(self, email: str, token: str, expires_hours: int = 1) -> bool:
        """Set password reset token"""
        expires = datetime.utcnow() + timedelta(hours=expires_hours)
        return self.update_user(
            email,
            reset_token=token,
            reset_token_expires=expires
        )
    
    def verify_reset_token(self, email: str, token: str) -> bool:
        """Verify password reset token"""
        user = self.get_user_by_email(email)
        if not user:
            return False
        
        if user.get('reset_token') == token:
            expires = user.get('reset_token_expires')
            if isinstance(expires, datetime) and expires > datetime.utcnow():
                return True
        return False
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{secrets.token_urlsafe(16)}"
    
    def _format_user_response(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format user data for response"""
        # Convert Firestore timestamps to ISO strings
        for field in ['join_date', 'last_login', 'created_at', 'reset_token_expires',
                     'assessment_package_expiry', 'subscription_expiry', 'updated_at']:
            if field in user_data and isinstance(user_data[field], datetime):
                user_data[field] = user_data[field].isoformat()
        
        # Remove password hash from response
        user_data.pop('password_hash', None)
        return user_data


class AssessmentDAL:
    """Assessment Data Access Layer using Firestore"""
    
    def __init__(self, connection: FirestoreConnection):
        self.conn = connection
        self.collection = connection.get_collection('assessments')
    
    def create_assessment(self, user_id: str, assessment_type: str, **kwargs) -> str:
        """Create new assessment"""
        assessment_id = f"assess_{secrets.token_urlsafe(16)}"
        
        assessment_data = {
            'assessment_id': assessment_id,
            'user_id': user_id,
            'assessment_type': assessment_type,
            'status': 'in_progress',
            'created_at': datetime.utcnow(),
            'completed_at': None,
            'score': None,
            'feedback': None,
            **kwargs
        }
        
        doc_ref = self.collection.document(assessment_id)
        doc_ref.set(assessment_data)
        return assessment_id
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment by ID"""
        try:
            doc = self.collection.document(assessment_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Failed to get assessment {assessment_id}: {e}")
            return None
    
    def get_user_assessments(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all assessments for a user"""
        try:
            assessments = self.collection.where(
                filter=FieldFilter('user_id', '==', user_id)
            ).order_by('created_at', direction=firestore.Query.DESCENDING)\
             .limit(limit).stream()
            
            return [a.to_dict() for a in assessments]
        except Exception as e:
            logger.error(f"Failed to get assessments for user {user_id}: {e}")
            return []
    
    def update_assessment(self, assessment_id: str, **updates) -> bool:
        """Update assessment"""
        try:
            updates['updated_at'] = datetime.utcnow()
            self.collection.document(assessment_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update assessment {assessment_id}: {e}")
            return False
    
    def complete_assessment(self, assessment_id: str, score: float, feedback: Dict) -> bool:
        """Mark assessment as complete"""
        return self.update_assessment(
            assessment_id,
            status='completed',
            completed_at=datetime.utcnow(),
            score=score,
            feedback=feedback
        )


class SessionDAL:
    """Session Data Access Layer using Firestore"""
    
    def __init__(self, connection: FirestoreConnection):
        self.conn = connection
        self.collection = connection.get_collection('sessions')
    
    def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        
        session_doc = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=1),
            **session_data
        }
        
        self.collection.document(session_id).set(session_doc)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            doc = self.collection.document(session_id).get()
            if doc.exists:
                session = doc.to_dict()
                # Check expiration
                if session['expires_at'] > datetime.utcnow():
                    return session
                else:
                    # Delete expired session
                    self.delete_session(session_id)
            return None
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            self.collection.document(session_id).delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (run periodically via Cloud Scheduler)"""
        try:
            now = datetime.utcnow()
            expired = self.collection.where(
                filter=FieldFilter('expires_at', '<', now)
            ).stream()
            
            for session in expired:
                session.reference.delete()
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")


class QRTokenDAL:
    """QR Token Data Access Layer using Firestore"""
    
    def __init__(self, connection: FirestoreConnection):
        self.conn = connection
        self.collection = connection.get_collection('qr_tokens')
    
    def create_qr_token(self, user_id: str, device_info: Dict = None) -> str:
        """Create QR code token"""
        token = secrets.token_urlsafe(32)
        
        qr_data = {
            'token': token,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=5),
            'used': False,
            'device_info': device_info or {}
        }
        
        self.collection.document(token).set(qr_data)
        return token
    
    def verify_qr_token(self, token: str) -> Optional[str]:
        """Verify QR token and return user_id"""
        try:
            doc = self.collection.document(token).get()
            if doc.exists:
                qr = doc.to_dict()
                if not qr['used'] and qr['expires_at'] > datetime.utcnow():
                    # Mark as used
                    doc.reference.update({'used': True})
                    return qr['user_id']
            return None
        except Exception as e:
            logger.error(f"Failed to verify QR token: {e}")
            return None


class EntitlementDAL:
    """User Entitlement (In-App Purchase) Data Access Layer"""
    
    def __init__(self, connection: FirestoreConnection):
        self.conn = connection
        self.collection = connection.get_collection('entitlements')
    
    def create_entitlement(self, user_id: str, product_id: str, 
                          receipt_data: Dict, platform: str) -> str:
        """Create entitlement from purchase"""
        entitlement_id = f"ent_{secrets.token_urlsafe(16)}"
        
        entitlement = {
            'entitlement_id': entitlement_id,
            'user_id': user_id,
            'product_id': product_id,
            'platform': platform,
            'receipt_data': receipt_data,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'expires_at': None  # For consumable products
        }
        
        self.collection.document(entitlement_id).set(entitlement)
        return entitlement_id
    
    def get_user_entitlements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active entitlements for user"""
        try:
            entitlements = self.collection.where(
                filter=FieldFilter('user_id', '==', user_id)
            ).where(
                filter=FieldFilter('status', '==', 'active')
            ).stream()
            
            return [e.to_dict() for e in entitlements]
        except Exception as e:
            logger.error(f"Failed to get entitlements for user {user_id}: {e}")
            return []
    
    def consume_entitlement(self, entitlement_id: str) -> bool:
        """Mark entitlement as consumed"""
        try:
            self.collection.document(entitlement_id).update({
                'status': 'consumed',
                'consumed_at': datetime.utcnow()
            })
            return True
        except Exception as e:
            logger.error(f"Failed to consume entitlement {entitlement_id}: {e}")
            return False
