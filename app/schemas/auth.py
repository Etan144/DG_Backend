from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str