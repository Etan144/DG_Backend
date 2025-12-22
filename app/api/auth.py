from fastapi import APIRouter
from app.schemas.auth import RegisterRequest, VerifyOtpRequest
from app.services.auth_service import register_user, verify_otp_code

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(request: RegisterRequest):
    return register_user(request)

@router.post("/verify-otp")
def verify_otp(request: VerifyOtpRequest):
    return verify_otp_code(request)
