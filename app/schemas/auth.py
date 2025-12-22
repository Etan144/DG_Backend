from pydantic import BaseModel, EmailStr, Field

# Fields used for basic validation during registration
# Stops monkeys from trying to inject bad data or malicious code

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(...,min_length=6)

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendOtpRequest(BaseModel):
    email: EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"