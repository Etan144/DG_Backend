from fastapi import APIRouter, Request
from app.schemas.auth import RegisterRequest, VerifyOtpRequest, ResendOtpRequest, LoginRequest, RefreshTokenRequest, TokenResponse
from app.services.auth_service import register_user, verify_otp_code, resend_otp_service, login_user
from app.core.security import decode_refresh_token, create_access_token
from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=dict)
@limiter.limit("3/minute")
def register(request: Request, auth_request: RegisterRequest):
    """Register a new user with email and password. Sends OTP verification email.
    
    Rate limit: 3 requests per minute
    """
    return register_user(auth_request)

@router.post("/verify-otp", response_model=dict)
def verify_otp(request: VerifyOtpRequest):
    """Verify OTP code and create user account."""
    return verify_otp_code(request)

@router.post("/resend-otp", response_model=dict)
@limiter.limit("5/minute")
def resend_otp(request: Request, auth_request: ResendOtpRequest):
    """Resend OTP code to email with rate limiting.
    
    Rate limit: 5 requests per minute
    """
    return resend_otp_service(auth_request)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, auth_request: LoginRequest):
    """Login with username and password. Returns access and refresh tokens.
    
    Rate limit: 5 requests per minute
    """
    return login_user(auth_request)

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
def refresh_token(request: Request, auth_request: RefreshTokenRequest):
    """Refresh access token using refresh token.
    
    Rate limit: 10 requests per minute
    """
    try:
        user_id = decode_refresh_token(auth_request.refresh_token)
        access_token = create_access_token(subject=user_id)
        return {
            "access_token": access_token,
            "refresh_token": auth_request.refresh_token,  # Refresh token remains the same
            "token_type": "bearer"
        }
    except HTTPException:
        raise
