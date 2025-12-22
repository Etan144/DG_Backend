import smtplib
from email.message import EmailMessage
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

def send_otp_email(to_email: str, otp: str) -> bool:
    """Send OTP email to user.
    
    Args:
        to_email: Recipient email address
        otp: One-time password code
        
    Returns:
        True if email sent successfully, raises HTTPException otherwise
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your OTP Code - DG Backend"
        msg["From"] = settings.smtp_email
        msg["To"] = to_email
        msg.set_content(f"Your OTP code is: {otp}\n\nThis code expires in 5 minutes.")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.smtp_email, settings.smtp_password)
            server.send_message(msg)
        
        logger.info(f"OTP email sent successfully to {to_email}")
        return True
    
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        raise Exception("Email service authentication failed")
    
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error while sending OTP to {to_email}: {e}")
        raise Exception("Failed to send OTP email")
    
    except Exception as e:
        logger.error(f"Unexpected error sending OTP to {to_email}: {e}")
        raise Exception("Unexpected error sending email")