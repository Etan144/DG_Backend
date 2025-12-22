from fastapi import APIRouter
from app.schemas.auth import RegisterRequest, VerifyOtpRequest, ResendOtpRequest, LoginRequest, TokenResponse
from app.services.auth_service import register_user, verify_otp_code, resend_otp_service, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(request: RegisterRequest):
    return register_user(request)

@router.post("/verify-otp")
def verify_otp(request: VerifyOtpRequest):
    return verify_otp_code(request)

@router.post("/resend-otp")
def resend_otp(request: ResendOtpRequest):
    return resend_otp_service(request)

@router.post("/login")
def login(request: LoginRequest, response_model = TokenResponse):
    return login_user(request)
