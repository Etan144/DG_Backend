import random
from datetime import datetime, timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError

from app.db.database import db
from app.services.email_service import send_otp_email
from app.core.security import create_access_token

otp_collection = db.otp
user_collection = db.users
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

max_resend_attemps = 5
resend_window_minutes = 10

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
            "hashed_password": record["hashed_password"],
            "verified": True,
            "created_at": datetime.utcnow()
        })
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")

    otp_collection.delete_one({"email": data.email})

    return {"message": "User account created"}


def resend_otp_service(data):
    record = otp_collection.find_one({"email": data.email})

    if not record:
        raise HTTPException(status_code=400, detail="No OTP request found for this email")
    
    now = datetime.utcnow()
    
    resend_count = record.get("resend_count", 0)
    last_resend_at = record.get("last_resend_at")

    #Rate limiting stuff
    if resend_count >= max_resend_attemps:
        if last_resend_at and (now - last_resend_at) < timedelta(minutes=resend_window_minutes):
            raise HTTPException(status_code=429, detail="Max resend attempts reached. Please try again later." )
        else:
            #Reset counter
            resend_count = 0
    

    #Generate new OTP
    new_otp = generate_otp()

    otp_collection.update_one(
        {"email": data.email},
        {
            "$set": {
                "otp": new_otp,
                "expires_at": now + timedelta(minutes=5),
                "last_resend_at": now
            },
            "$inc": {"resend_count": 1}
        }   
    )

    send_otp_email(data.email,new_otp)

    return {"message": "OTP resent successfully"}


def login_user(data):
    user = user_collection.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(subject = str(user["_id"]))
    
    return {"access_token": access_token, "token_type": "bearer"}
