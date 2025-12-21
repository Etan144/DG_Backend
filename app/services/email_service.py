import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP Code"
    msg["From"] = settings.smtp_email
    msg["To"] = to_email
    msg.set_content(f"Your OTP code is: {otp}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.smtp_email, settings.smtp_password)
        server.send_message(msg)