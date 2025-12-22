from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

def send_otp_email(to_email: str, otp: str) -> bool:
    """Send OTP email to user using SendGrid.
    
    Args:
        to_email: Recipient email address
        otp: One-time password code
        
    Returns:
        True if email sent successfully, raises Exception otherwise
    """
    try:
        message = Mail(
            from_email=settings.sendgrid_from_email if hasattr(settings, 'sendgrid_from_email') else 'noreply@deepfakeguard.com',
            to_emails=to_email,
            subject='Your OTP Code - Deepfake Guard',
            plain_text_content=f"""Your OTP code is: {otp}

This code expires in 5 minutes.

If you didn't request this code, please ignore this email.

Best regards,
Deepfake Guard Team""",
            html_content=f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 500px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #333; margin-bottom: 20px;">Deepfake Guard - OTP Verification</h2>
                        <p style="color: #666; font-size: 16px; margin-bottom: 20px;">Your one-time password is:</p>
                        <div style="background-color: #f0f0f0; padding: 15px; border-radius: 4px; text-align: center; margin-bottom: 20px;">
                            <h1 style="color: #2c3e50; margin: 0; font-size: 32px; letter-spacing: 2px;">{otp}</h1>
                        </div>
                        <p style="color: #999; font-size: 14px; margin-bottom: 20px;">This code expires in <strong>5 minutes</strong>.</p>
                        <hr style="border: none; border-top: 1px solid #e0e0e0; margin-bottom: 20px;">
                        <p style="color: #999; font-size: 12px;">If you didn't request this code, please ignore this email.</p>
                        <p style="color: #999; font-size: 12px;">Best regards,<br/>Deepfake Guard Team</p>
                    </div>
                </body>
            </html>
            """
        )
        
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)
        
        logger.info(f"OTP email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"SendGrid error while sending OTP to {to_email}: {e}")
        raise Exception(f"Failed to send OTP email: {str(e)}")