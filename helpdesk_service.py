"""
IELTS AI Prep - Helpdesk Email Service  
Handles automatic email responses for helpdesk@ieltsaiprep.com
Includes AI-powered ticket analysis and response generation using Gemini 2.5 Flash
"""

import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from ai_helpdesk_knowledge_base import get_ai_response_guidelines

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARN] Google Gemini SDK not available - using fallback responses")


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
    
    # TODO: Store in DynamoDB for persistent tracking
    # For now, just log it
    print(f"[HELPDESK] New ticket created: {ticket_id}")
    print(f"[HELPDESK] From: {user_email}")
    print(f"[HELPDESK] Subject: {message_subject}")
    
    return ticket_data


def analyze_ticket_with_ai(ticket_subject: str, ticket_body: str, user_metadata: dict = None) -> dict:
    """
    Use Gemini 2.5 Flash to analyze helpdesk ticket and generate AI response
    
    Args:
        ticket_subject: Subject line of ticket
        ticket_body: Main content of ticket
        user_metadata: Optional user context (purchase history, etc.)
    
    Returns:
        dict: {
            'category': str,  # technical, purchase, account, score_dispute, refund, etc.
            'confidence': float,  # 0.0 to 1.0
            'suggested_response': str,  # AI-generated response
            'requires_human': bool,  # True if should escalate to human
            'escalation_reason': str  # Why it needs human review
        }
    """
    try:
        # Check if Gemini API key is available
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            print("[WARN] GEMINI_API_KEY not configured - AI analysis unavailable")
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'suggested_response': '',
                'requires_human': True,
                'escalation_reason': 'AI service unavailable'
            }
        
        # Get knowledge base and guidelines
        guidelines = get_ai_response_guidelines()
        knowledge_base = json.dumps(guidelines['knowledge_base'], indent=2)
        personality = guidelines['personality']
        templates = json.dumps(guidelines['templates'], indent=2)
        
        # Build AI prompt
        user_context = json.dumps(user_metadata, indent=2) if user_metadata else "No user data available"
        
        prompt = f"""You are an AI support agent for IELTS AI Prep. Analyze this support ticket and provide a helpful response.

KNOWLEDGE BASE:
{knowledge_base}

PERSONALITY GUIDELINES:
{personality}

RESPONSE TEMPLATES:
{templates}

USER CONTEXT:
{user_context}

SUPPORT TICKET:
Subject: {ticket_subject}
Body: {ticket_body}

TASK:
1. Categorize this ticket (technical, purchase, account, score_dispute, refund_request, general_inquiry, feature_request, complaint)
2. Determine if it can be handled by AI (confidence score 0.0-1.0)
3. Generate a polite, helpful, professional response following the personality guidelines
4. Determine if human escalation is needed

Respond in JSON format:
{{
    "category": "category_name",
    "confidence": 0.0-1.0,
    "suggested_response": "your friendly, helpful response here",
    "requires_human": true/false,
    "escalation_reason": "reason if requires_human is true, empty string otherwise"
}}

IMPORTANT RULES:
- Be warm, friendly, and empathetic - NEVER curt
- Use simple, everyday language
- For refunds WITHOUT technical issues: AI handles with policy response (requires_human=false)
- For refunds WITH technical failures: Escalate for investigation (requires_human=true)
- For score disputes WITHOUT technical issues: AI handles with policy response (requires_human=false)
- For score disputes WITH technical failures: Escalate for investigation (requires_human=true)
- For technical issues: Provide step-by-step troubleshooting (AI handles, requires_human=false)
- Escalate ONLY if: legal/compliance matters, technical failures, complex complaints, uncertain about answer

DECISION LOGIC:
- Refund request + no technical issue = AI handles (requires_human=false)
- Refund request + technical issue = Escalate (requires_human=true)
- Score dispute + no technical issue = AI handles (requires_human=false)
- Score dispute + technical issue = Escalate (requires_human=true)
- Technical support = AI handles (requires_human=false)"""

        # Try Gemini AI first, fallback to rule-based if unavailable
        if GEMINI_AVAILABLE:
            try:
                # Initialize Gemini client
                project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
                if project_id:
                    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
                    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
                    client = genai.Client()
                else:
                    client = genai.Client(api_key=gemini_api_key)
                
                # Call Gemini 2.5 Flash API
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                        temperature=0.7,
                        max_output_tokens=1024
                    )
                )
                
                result = json.loads(response.text)
                print(f"[AI_HELPDESK] Gemini analyzed ticket: {result.get('category', 'unknown')}")
                return result
                
            except Exception as e:
                print(f"[WARN] Gemini API call failed, using fallback: {str(e)}")
        
        # Fallback: Simple rule-based categorization
        print(f"[AI_HELPDESK] Using fallback rule-based analysis")
        subject_lower = ticket_subject.lower()
        body_lower = ticket_body.lower()
        
        if any(word in subject_lower + body_lower for word in ['refund', 'money back', 'cancel']):
            category = 'refund_request'
            confidence = 0.9
            # AI can handle with clear policy response - only escalate if technical failure mentioned
            has_technical_issue = any(word in body_lower for word in ['error', 'crash', 'broken', 'not working', 'failed', 'malfunction', 'blank', 'incomplete'])
            requires_human = has_technical_issue
            escalation_reason = 'Possible technical failure - needs investigation' if has_technical_issue else ''
        elif any(word in subject_lower + body_lower for word in ['score', 'unfair', 'wrong', 'disagree']):
            category = 'score_dispute'
            confidence = 0.85
            # AI can handle with policy response - only escalate if technical failure mentioned
            has_technical_issue = any(word in body_lower for word in ['error', 'crash', 'broken', 'not working', 'failed', 'malfunction', 'blank', 'incomplete', 'froze', 'cut off'])
            requires_human = has_technical_issue
            escalation_reason = 'Possible technical failure during assessment - needs investigation' if has_technical_issue else ''
        elif any(word in subject_lower + body_lower for word in ['login', 'password', 'access', 'qr', 'technical', 'error', 'not working']):
            category = 'technical'
            confidence = 0.8
            requires_human = False
        elif any(word in subject_lower + body_lower for word in ['purchase', 'payment', 'buy', 'receipt']):
            category = 'purchase'
            confidence = 0.8
            requires_human = False
        else:
            category = 'general_inquiry'
            confidence = 0.7
            requires_human = False
        
        suggested_response = f"""Subject: Re: {ticket_subject}

{_get_template_response(category, ticket_body)}"""
        
        return {
            'category': category,
            'confidence': confidence,
            'suggested_response': suggested_response,
            'requires_human': requires_human,
            'escalation_reason': escalation_reason if requires_human else ''
        }
        
    except Exception as e:
        print(f"[ERROR] AI ticket analysis failed: {str(e)}")
        return {
            'category': 'error',
            'confidence': 0.0,
            'suggested_response': '',
            'requires_human': True,
            'escalation_reason': f'AI analysis error: {str(e)}'
        }


def _get_template_response(category: str, ticket_body: str) -> str:
    """Get appropriate template response based on ticket category"""
    responses = {
        'refund_request': """Thank you for contacting us regarding your refund request.

As per our Terms and Conditions (accepted at registration), all purchases are final and non-refundable. This policy was outlined before purchase completion.

If you experienced a technical issue during your assessment, please provide specific details so we can investigate.

Best regards,
IELTS AI Prep Support""",
        
        'score_dispute': """Thank you for contacting us about your assessment score.

All AI-generated scores are final. As stated in our Terms of Service (accepted at registration), we do not offer manual review, score reassessment, or score adjustments.

If you experienced a technical issue during your assessment, please provide specific details so we can investigate.

Best regards,
IELTS AI Prep Support""",
        
        'technical': """Thank you for reporting this technical issue.

To assist you quickly, please provide:
• Specific error message (if any)
• Browser you're using
• When the issue started

Quick troubleshooting steps to try:
1. Clear browser cache and cookies
2. Try Chrome or Safari browser
3. Check internet connection stability
4. Update your browser to latest version

Please reply with the details above, and I'll provide a solution.

Best regards,
IELTS AI Prep Support""",
        
        'purchase': """Thank you for contacting us about your purchase.

Receipt validation typically takes 1-2 minutes. Please try:
1. Refresh the page or logout/login again
2. Verify the purchase email matches your login email
3. Check your app store receipt confirms the purchase

If the issue persists, please reply with:
• Receipt number from app store
• Email address used for purchase
• Date and time of purchase

I'll investigate and ensure you get access.

Best regards,
IELTS AI Prep Support""",
        
        'general_inquiry': """Thank you for contacting IELTS AI Prep.

I'm happy to help with your question. Please provide more details about what you need, and I'll respond with the information you're looking for.

Best regards,
IELTS AI Prep Support"""
    }
    
    return responses.get(category, "I've received your message and I'm here to help. Let me look into this for you.")


def send_escalation_email(ticket_data: dict, ai_analysis: dict) -> bool:
    """
    Send escalation email to human support team when AI cannot handle ticket
    
    Args:
        ticket_data: Original ticket information
        ai_analysis: AI analysis results
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        # Check if running in development mode
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            print(f"[DEV_MODE] Escalation email would be sent for ticket: {ticket_data.get('ticket_id')}")
            return True
        
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        escalation_email = os.environ.get('HELPDESK_ESCALATION_EMAIL')
        
        if not sendgrid_api_key or not escalation_email:
            print("[ERROR] SendGrid or escalation email not configured")
            return False
        
        ticket_id = ticket_data.get('ticket_id', 'UNKNOWN')
        user_email = ticket_data.get('user_email', 'unknown@example.com')
        subject = ticket_data.get('subject', 'No Subject')
        body = ticket_data.get('body', 'No content')
        category = ai_analysis.get('category', 'unknown')
        escalation_reason = ai_analysis.get('escalation_reason', 'AI unable to handle')
        
        email_subject = f"[ESCALATION] IELTS AI Prep Support - {ticket_id}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Support Escalation - {ticket_id}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="background: #E33219; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">⚠️ Support Ticket Escalation</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
                <h2 style="color: #E33219; margin-top: 0;">Ticket Details</h2>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <tr style="background: white;">
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #dee2e6;">Ticket ID:</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">{ticket_id}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #dee2e6;">User Email:</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">{user_email}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #dee2e6;">Category:</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">{category}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #dee2e6;">Timestamp:</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">{ticket_data.get('timestamp', 'N/A')}</td>
                    </tr>
                </table>
                
                <h3 style="color: #E33219;">Escalation Reason</h3>
                <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #E33219; margin-bottom: 20px;">
                    <p style="margin: 0; color: #856404;"><strong>{escalation_reason}</strong></p>
                </div>
                
                <h3 style="color: #E33219;">Original Message</h3>
                <div style="background: white; padding: 15px; border: 1px solid #dee2e6; border-radius: 4px; margin-bottom: 20px;">
                    <p style="margin: 0 0 10px 0;"><strong>Subject:</strong> {subject}</p>
                    <p style="margin: 0; white-space: pre-wrap;">{body}</p>
                </div>
                
                <h3 style="color: #E33219;">AI-Suggested Response (Review Before Sending)</h3>
                <div style="background: white; padding: 15px; border: 1px solid #dee2e6; border-radius: 4px;">
                    <p style="margin: 0; white-space: pre-wrap;">{ai_analysis.get('suggested_response', 'No response generated')}</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #dee2e6;">
                    <p style="color: #666; font-size: 14px; margin: 0;">
                        <strong>Action Required:</strong> Please review this ticket and respond to the user at {user_email} within 5-7 business days.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
SUPPORT TICKET ESCALATION

Ticket ID: {ticket_id}
User Email: {user_email}
Category: {category}
Timestamp: {ticket_data.get('timestamp', 'N/A')}

ESCALATION REASON:
{escalation_reason}

ORIGINAL MESSAGE:
Subject: {subject}

{body}

AI-SUGGESTED RESPONSE (Review before sending):
{ai_analysis.get('suggested_response', 'No response generated')}

---
Action Required: Please review this ticket and respond to the user at {user_email} within 5-7 business days.
        """
        
        message = Mail(
            from_email='helpdesk@ieltsaiprep.com',
            to_emails=escalation_email,
            subject=email_subject,
            html_content=html_body
        )
        message.add_content(text_body, 'text/plain')
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        print(f"[SendGrid] Escalation email sent for {ticket_id}: Status {response.status_code}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send escalation email: {str(e)}")
        return False
