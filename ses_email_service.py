"""
AWS SES Email Service
Handles all email operations using Amazon Simple Email Service
"""
import boto3
from botocore.exceptions import ClientError
import os
from typing import Dict, Optional

class SESEmailService:
    """AWS SES Email Service for IELTS AI Prep"""
    
    def __init__(self):
        """Initialize SES client"""
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.ses_client = boto3.client('ses', region_name=self.region)
        self.sender_email = os.environ.get('SES_SENDER_EMAIL', 'noreply@ieltsaiprep.com')
        self.domain_url = os.environ.get('DOMAIN_URL', 'https://ieltsaiprep.com')
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send email via AWS SES
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content of the email
            text_body: Plain text content (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Build the email message
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
            }
            
            # Add text body if provided
            if text_body:
                message['Body']['Text'] = {'Data': text_body, 'Charset': 'UTF-8'}
            
            # Send the email
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [to_email]},
                Message=message
            )
            
            print(f"[SES] Email sent to {to_email}: MessageId {response['MessageId']}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'MessageRejected':
                print(f"[SES] Email rejected: {error_message}")
            elif error_code == 'MailFromDomainNotVerified':
                print(f"[SES] Sender domain not verified: {self.sender_email}")
            elif error_code == 'ConfigurationSetDoesNotExist':
                print(f"[SES] Configuration set does not exist")
            else:
                print(f"[SES] Error sending email: {error_code} - {error_message}")
            
            return False
            
        except Exception as e:
            print(f"[SES] Unexpected error: {str(e)}")
            return False
    
    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: User's email address
            reset_token: Password reset token
        
        Returns:
            bool: True if email sent successfully
        """
        reset_link = f"{self.domain_url}/reset_password?token={reset_token}"
        
        subject = "Password Reset - IELTS AI Prep"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e9ecef;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a request to reset your password for your IELTS AI Prep account.</p>
                <p>Click the button below to reset your password:</p>
                <div style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #3498db;">{reset_link}</p>
                <p><strong>This link will expire in 1 hour for security reasons.</strong></p>
                <p>If you didn't request a password reset, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2025 IELTS AI Prep. All rights reserved.</p>
                <p>This is an automated message, please do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hello,
        
        We received a request to reset your password for your IELTS AI Prep account.
        
        To reset your password, please visit:
        {reset_link}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        IELTS AI Prep Team
        """
        
        return self.send_email(email, subject, html_body, text_body)
    
    def send_verification_email(self, email: str, verification_token: str) -> bool:
        """
        Send email verification
        
        Args:
            email: User's email address
            verification_token: Email verification token
        
        Returns:
            bool: True if email sent successfully
        """
        verify_link = f"{self.domain_url}/verify_email?token={verification_token}"
        
        subject = "Verify Your Email - IELTS AI Prep"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e9ecef;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #27ae60;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to IELTS AI Prep!</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Thank you for registering with IELTS AI Prep, your AI-powered IELTS preparation platform.</p>
                <p>Please verify your email address by clicking the button below:</p>
                <div style="text-align: center;">
                    <a href="{verify_link}" class="button">Verify Email</a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #3498db;">{verify_link}</p>
                <p>Once verified, you'll have access to:</p>
                <ul>
                    <li>AI-powered Speaking assessments with real-time feedback</li>
                    <li>Writing task evaluation with detailed band scores</li>
                    <li>Full-length practice tests for Listening and Reading</li>
                    <li>Personalized improvement recommendations</li>
                </ul>
                <p><strong>This verification link will expire in 24 hours.</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 IELTS AI Prep. All rights reserved.</p>
                <p>This is an automated message, please do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to IELTS AI Prep!
        
        Thank you for registering with IELTS AI Prep, your AI-powered IELTS preparation platform.
        
        Please verify your email address by visiting:
        {verify_link}
        
        Once verified, you'll have access to:
        - AI-powered Speaking assessments with real-time feedback
        - Writing task evaluation with detailed band scores
        - Full-length practice tests for Listening and Reading
        - Personalized improvement recommendations
        
        This verification link will expire in 24 hours.
        
        Best regards,
        IELTS AI Prep Team
        """
        
        return self.send_email(email, subject, html_body, text_body)
    
    def test_connection(self) -> Dict:
        """
        Test SES connection and configuration
        
        Returns:
            Dict: Status information
        """
        try:
            # Get send quota
            quota = self.ses_client.get_send_quota()
            
            # Get verified identities
            identities = self.ses_client.list_verified_email_addresses()
            
            return {
                'status': 'connected',
                'region': self.region,
                'sender_email': self.sender_email,
                'send_quota': {
                    'max_24hour_send': quota.get('Max24HourSend', 0),
                    'sent_last_24hours': quota.get('SentLast24Hours', 0),
                    'max_send_rate': quota.get('MaxSendRate', 0)
                },
                'verified_emails': identities.get('VerifiedEmailAddresses', [])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Initialize global instance
ses_service = SESEmailService()