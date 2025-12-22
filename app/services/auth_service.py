import random
from datetime import datetime, timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from pymongo import DuplicateKeyError
from app.db.database import db
from app.services.email_service import send_otp_email

otp_collection = db.otp
user_collection = db.users
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def register_user(data):
    # Check if user already exists
    if user_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Remove any existing OTPs for this email 
    # Prevents replay attacks
    otp_collection.delete_many({"email": data.email})

    otp = generate_otp()

    hashed_password = pwd_context.hash(data.password)

    # Store OTP temporarily
    otp_collection.insert_one({
        "username": data.username,
        "email": data.email,
        "hashed_password": hashed_password,
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "resend_count": 0,
        "last_resend_at": datetime.utcnow()
    })

    send_otp_email(data.email, otp)

    return {"message": "OTP sent to email"}


def verify_otp_code(data):
    record = otp_collection.find_one({
        "email": data.email,
        "otp": data.otp,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    try:
        # Create user
        user_collection.insert_one({
            "username": record["username"],
            "email": record["email"],
            "password": record["hashed_password"],
            "verified": True,
            "created_at": datetime.utcnow()
        })
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")

    otp_collection.delete_one({"email": data.email})

    return {"message": "User account created"}
