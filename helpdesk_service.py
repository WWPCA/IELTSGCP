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
- For refunds: Show empathy, explain policy gently, offer technical support
- For score disputes: Acknowledge frustration, explain AI limitations kindly, check for technical issues
- For technical issues: Provide step-by-step troubleshooting
- Escalate if: legal/compliance matters, complex complaints, uncertain about answer"""

        # TODO: Call Gemini 2.5 Flash API here
        # For now, return a template response
        print(f"[AI_HELPDESK] Would analyze ticket with Gemini API")
        print(f"[AI_HELPDESK] Subject: {ticket_subject}")
        
        # Simple rule-based categorization for now
        subject_lower = ticket_subject.lower()
        body_lower = ticket_body.lower()
        
        if any(word in subject_lower + body_lower for word in ['refund', 'money back', 'cancel']):
            category = 'refund_request'
            confidence = 0.9
            requires_human = True
            escalation_reason = 'Refund requests require human review per policy'
        elif any(word in subject_lower + body_lower for word in ['score', 'unfair', 'wrong', 'disagree']):
            category = 'score_dispute'
            confidence = 0.85
            requires_human = True
            escalation_reason = 'Score disputes may need technical investigation'
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
        
        suggested_response = f"""Hello! Thank you for contacting IELTS AI Prep support.

I've received your message about: {ticket_subject}

{_get_template_response(category, ticket_body)}

Is there anything else I can help you with? We're here to support your IELTS preparation journey!

Best regards,
IELTS AI Prep Support Team
helpdesk@ieltsaiprep.com"""
        
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
        'refund_request': """I understand your frustration, and I genuinely want to help. Our policy states that all purchases are final and non-refundable, as outlined in our Terms of Service. 

However, if you experienced a technical failure during your assessment (such as system errors, audio not recording, or incomplete feedback), we can certainly look into that. Could you please describe what happened during your assessment?

Technical issues we can help with:
• System failure to process your submission
• Audio/text not recorded due to platform malfunction
• Blank feedback or incomplete scoring

I'm here to ensure you get the support you deserve.""",
        
        'score_dispute': """Thank you for sharing your concerns about your assessment results. I understand it can be disappointing when scores don't meet expectations, and I want to help clarify how our system works.

Our AI assessment provides practice scores based on IELTS criteria. While these scores are final as generated by the AI system, I want to ensure you had a proper technical experience.

Were there any technical issues during your assessment, such as:
• Audio problems or cutting out
• System errors or freezing
• Incomplete feedback display

If you experienced any technical difficulties, please let me know and I'll investigate right away.""",
        
        'technical': """I'm sorry to hear you're experiencing technical difficulties. Let's work together to resolve this.

Could you please provide a bit more detail about what's happening? This will help me give you the most accurate solution:
• What specific error message are you seeing (if any)?
• Which browser are you using?
• When did this issue first occur?

In the meantime, here are some quick troubleshooting steps:
1. Clear your browser cache and cookies
2. Try a different browser (Chrome or Safari recommended)
3. Ensure your internet connection is stable
4. Check that your browser is up to date

I'm here to help get this resolved for you!""",
        
        'purchase': """I understand how concerning it is when your purchase doesn't appear right away. Let's get this sorted out for you.

Receipt validation typically takes 1-2 minutes, but sometimes it can take a bit longer. Here's what I recommend:

1. Refresh the page or logout and login again
2. Verify the purchase was made with the email address you're currently logged in with
3. Check your app store receipt to confirm the purchase went through

If the issue persists after trying these steps, please reply with:
• Your receipt number from the app store
• The email address used for the purchase
• When the purchase was made

I'll investigate this right away and ensure you get access to your assessments!""",
        
        'general_inquiry': """Thank you for your question! I'm here to help provide the information you need for your IELTS preparation.

Let me address your inquiry..."""
    }
    
    return responses.get(category, "I've received your message and I'm here to help. Let me look into this for you.")
