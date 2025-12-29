import random
from datetime import datetime, timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError

from app.db.database import db
from app.services.email_service import send_otp_email
from app.core.security import create_tokens
from app.core.logging import get_logger

logger = get_logger(__name__)

otp_collection = db.otp
user_collection = db.users
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

max_resend_attemps = 5
resend_window_minutes = 10

def generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def register_user(data):
    """Register a new user and send OTP verification email.
    
    Args:
        data: RegisterRequest containing username, email, password
        
    Returns:
        dict with success message
        
    Raises:
        HTTPException: If user already exists or email service fails
    """
    try:
        # Check if user already exists
        if user_collection.find_one({"email": data.email}):
            logger.warning(f"Registration attempt for existing email: {data.email}")
            raise HTTPException(status_code=409, detail="User already exists")
        
        if user_collection.find_one({"username":data.username}):
            raise HTTPException(status_code=409, detail="Username already exists")
        
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

        # Send OTP email
        try:
            send_otp_email(data.email, otp)
            logger.info(f"User registration initiated for email: {data.email}")
        except Exception as e:
            # Clean up OTP record if email fails
            otp_collection.delete_one({"email": data.email})
            logger.error(f"Failed to send OTP for registration {data.email}: {e}")
            raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

        return {"message": "OTP sent to email"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration for {data.email}: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


def verify_otp_code(data):
    """Verify OTP code and create user account.
    
    Args:
        data: VerifyOtpRequest containing email and otp
        
    Returns:
        dict with success message
        
    Raises:
        HTTPException: If OTP is invalid, expired, or user creation fails
    """
    try:
        record = otp_collection.find_one({
            "email": data.email,
            "otp": data.otp,
            "expires_at": {"$gt": datetime.utcnow()}
        })

        if not record:
            logger.warning(f"Invalid OTP attempt for email: {data.email}")
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        try:
            # Create user
            user_collection.insert_one({
                "username": record["username"],
                "email": record["email"],
                "hashed_password": record["hashed_password"],
                "role": "RegisteredUser",
                "plan_tier": "free",
                "verified": True,
                "created_at": datetime.utcnow()
            })
            logger.info(f"User account created for email: {data.email}")
        except DuplicateKeyError as e:

            error_msg = str(e)

            if "username" in error_msg:
                raise HTTPException(
                    status_code =409,
                    detail = "Username already exists"
                )
            elif "email" in error_msg:
                raise HTTPException(
                    status_code=409, detail = "Email already exists"
                )
            else:
                logger.warning(f"User already exists during OTP verification: {data.email}")
                raise HTTPException(status_code=409, detail="User already exists")

        # Clean up OTP record
        otp_collection.delete_one({"email": data.email})

        return {"message": "User account created"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP for {data.email}: {e}")
        raise HTTPException(status_code=500, detail="OTP verification failed. Please try again.")


def resend_otp_service(data):
    """Resend OTP to user email with rate limiting.
    
    Args:
        data: ResendOtpRequest containing email
        
    Returns:
        dict with success message
        
    Raises:
        HTTPException: If no OTP request found, rate limit exceeded, or email fails
    """
    try:
        record = otp_collection.find_one({"email": data.email})

        if not record:
            logger.warning(f"Resend OTP attempt for non-existent request: {data.email}")
            raise HTTPException(status_code=400, detail="No OTP request found for this email")
        
        now = datetime.utcnow()
        resend_count = record.get("resend_count", 0)
        last_resend_at = record.get("last_resend_at")

        # Rate limiting
        if resend_count >= max_resend_attemps:
            if last_resend_at and (now - last_resend_at) < timedelta(minutes=resend_window_minutes):
                logger.warning(f"Resend OTP rate limit exceeded for {data.email}")
                raise HTTPException(status_code=429, detail="Max resend attempts reached. Please try again later.")
            else:
                # Reset counter after window
                resend_count = 0

        # Generate new OTP
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

        # Send OTP email
        try:
            send_otp_email(data.email, new_otp)
            logger.info(f"OTP resent successfully to {data.email}")
        except Exception as e:
            logger.error(f"Failed to resend OTP to {data.email}: {e}")
            raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

        return {"message": "OTP resent successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending OTP to {data.email}: {e}")
        raise HTTPException(status_code=500, detail="Resend failed. Please try again.")


def login_user(data):
    """Authenticate user and return access and refresh tokens.
    
    Args:
        data: LoginRequest containing email and password
        
    Returns:
        dict with access_token, refresh_token, and token_type
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        user = user_collection.find_one({"email": data.email})
        if not user or not pwd_context.verify(data.password, user["hashed_password"]):
            logger.warning(f"Failed login attempt for email: {data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        tokens = create_tokens(subject=str(user["_id"]))
        logger.info(f"User logged in successfully: {data.email}")
        
        return tokens
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login for {data.email}: {e}")
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")
