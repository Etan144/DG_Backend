import random
from app.db.database import db
from app.services.email_service import send_otp_email

otp_collection = db.otp
user_collection = db.users


def generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def register_user(data):
    # Check if user already exists
    if user_collection.find_one({"email": data.email}):
        return {"error": "User already exists"}

    otp = generate_otp()

    # Store OTP temporarily
    otp_collection.insert_one({
        "email": data.email,
        "otp": otp
    })

    send_otp_email(data.email, otp)

    return {"message": "OTP sent to email"}


def verify_otp_code(data):
    record = otp_collection.find_one({
        "email": data.email,
        "otp": data.otp
    })

    if not record:
        return {"error": "Invalid OTP"}

    # Create user
    user_collection.insert_one({
        "email": data.email,
        "password": "TEMP_PLAIN_TEXT",  # TODO: hash later
        "verified": True
    })

    otp_collection.delete_one({"email": data.email})

    return {"message": "User account created"}
