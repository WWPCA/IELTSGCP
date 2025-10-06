"""
IELTS AI Prep - Helpdesk Email Service
Handles automatic email responses for helpdesk@ieltsaiprep.com
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime


def send_helpdesk_auto_reply(user_email: str, user_name: str = None) -> bool:
    """
    Send automatic acknowledgment email when user contacts helpdesk@ieltsaiprep.com
    
    Args:
        user_email: User's email address
        user_name: Optional user name (extracted from email if not provided)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Check if running in development mode
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            print(f"[DEV_MODE] Helpdesk auto-reply would be sent to: {user_email}")
            return True
        
        # Production mode - use SendGrid
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_api_key:
            print("[ERROR] SENDGRID_API_KEY not configured")
            return False
        
        # Extract name from email if not provided
        if not user_name:
            user_name = user_email.split('@')[0].title()
        
        subject = "We've Received Your Message - IELTS AI Prep Support"
        
        # Professional HTML email template with IELTS AI Prep branding
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Support Ticket Received - IELTS AI Prep</title>
        </head>
        <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: #ffffff; text-align: center; padding: 30px 20px; border-radius: 8px 8px 0 0; border-bottom: 3px solid #E33219;">
                    <h1 style="color: #E33219; margin: 0 0 10px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.02em;">IELTS AI Prep</h1>
                    <p style="color: #666; margin: 0; font-size: 14px;">Your Personalized Path to IELTS Success</p>
                </div>
                
                <!-- Main Content -->
                <div style="background: #ffffff; padding: 40px 30px; border-radius: 0 0 8px 8px;">
                    <h2 style="color: #1a1a1a; font-weight: 600; margin-bottom: 20px; font-size: 22px;">Thank You for Contacting Us</h2>
                    
                    <p style="margin-bottom: 20px; color: #333;">Dear {user_name},</p>
                    
                    <p style="margin-bottom: 25px; color: #333;">We have successfully received your message and appreciate you reaching out to our support team.</p>
                    
                    <!-- Ticket Information Box -->
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #E33219; margin: 25px 0;">
                        <p style="margin: 0 0 10px 0; color: #1a1a1a; font-weight: 600; font-size: 16px;">
                            📋 Support Ticket Confirmed
                        </p>
                        <p style="margin: 0; color: #666; font-size: 14px;">
                            <strong>Received:</strong> {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}<br>
                            <strong>Response Time:</strong> Within 5-7 business days
                        </p>
                    </div>
                    
                    <p style="margin-bottom: 20px; color: #333;">Our support team will carefully review your inquiry and get back to you within <strong>5 to 7 business days</strong> with a comprehensive response.</p>
                    
                    <!-- What to Expect -->
                    <div style="background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e5e5e5; margin: 25px 0;">
                        <p style="margin: 0 0 15px 0; color: #1a1a1a; font-weight: 600; font-size: 16px;">
                            What Happens Next?
                        </p>
                        <ul style="margin: 0; padding-left: 20px; color: #333;">
                            <li style="margin-bottom: 8px;">Our support team will review your message</li>
                            <li style="margin-bottom: 8px;">We'll investigate your inquiry thoroughly</li>
                            <li style="margin-bottom: 8px;">You'll receive a detailed response via email</li>
                            <li>For urgent matters, we may contact you sooner</li>
                        </ul>
                    </div>
                    
                    <!-- Need Immediate Help? -->
                    <div style="background: #e6f3ff; padding: 16px; border-radius: 8px; border-left: 4px solid #0891B2; margin: 25px 0;">
                        <p style="margin: 0 0 10px 0; color: #1a1a1a; font-weight: 600; font-size: 14px;">
                            💡 Need Immediate Help?
                        </p>
                        <p style="margin: 0; color: #666; font-size: 14px;">
                            While you wait, check out our <strong>FAQ section</strong> or browse common solutions on our website. Many questions can be answered instantly!
                        </p>
                    </div>
                    
                    <p style="margin-bottom: 0; color: #333;">We're committed to providing you with the best support experience possible and helping you achieve your IELTS goals.</p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 30px 0;">
                    
                    <div style="text-align: center; margin-top: 35px;">
                        <p style="margin-bottom: 5px; font-weight: 600; color: #1a1a1a;">Best regards,</p>
                        <p style="margin-bottom: 15px; color: #333;">The IELTS AI Prep Support Team</p>
                        <p style="font-size: 12px; color: #999;">📧 helpdesk@ieltsaiprep.com</p>
                        <p style="font-size: 12px; color: #999;">© 2025 IELTS AI Prep. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text version for email clients that don't support HTML
        text_body = f"""
IELTS AI Prep - Support Ticket Received

Dear {user_name},

We have successfully received your message and appreciate you reaching out to our support team.

SUPPORT TICKET CONFIRMED
Received: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}
Response Time: Within 5-7 business days

Our support team will carefully review your inquiry and get back to you within 5 to 7 business days with a comprehensive response.

WHAT HAPPENS NEXT?
- Our support team will review your message
- We'll investigate your inquiry thoroughly
- You'll receive a detailed response via email
- For urgent matters, we may contact you sooner

NEED IMMEDIATE HELP?
While you wait, check out our FAQ section or browse common solutions on our website. Many questions can be answered instantly!

We're committed to providing you with the best support experience possible and helping you achieve your IELTS goals.

Best regards,
The IELTS AI Prep Support Team

helpdesk@ieltsaiprep.com
© 2025 IELTS AI Prep. All rights reserved.
        """
        
        # Send email via SendGrid
        message = Mail(
            from_email='helpdesk@ieltsaiprep.com',
            to_emails=user_email,
            subject=subject,
            html_content=html_body
        )
        message.add_content(text_body, 'text/plain')
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        print(f"[SendGrid] Helpdesk auto-reply sent to {user_email}: Status {response.status_code}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send helpdesk auto-reply: {str(e)}")
        return False


def log_helpdesk_ticket(user_email: str, message_subject: str, message_body: str, user_metadata: dict = None) -> dict:
    """
    Log helpdesk ticket for tracking and potential AI agent processing
    
    Args:
        user_email: User's email address
        message_subject: Subject of the user's message
        message_body: Body of the user's message
        user_metadata: Optional metadata about the user (purchase history, account status, etc.)
    
    Returns:
        dict: Ticket information including ticket_id, timestamp, and categorization
    """
    import uuid
    
    ticket_id = f"IELTS-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    ticket_data = {
        'ticket_id': ticket_id,
        'user_email': user_email,
        'subject': message_subject,
        'body': message_body,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'pending',
        'priority': 'normal',
        'metadata': user_metadata or {}
    }
    
    # TODO: Store in Firestore for persistent tracking
    # For now, just log it
    print(f"[HELPDESK] New ticket created: {ticket_id}")
    print(f"[HELPDESK] From: {user_email}")
    print(f"[HELPDESK] Subject: {message_subject}")
    
    return ticket_data
