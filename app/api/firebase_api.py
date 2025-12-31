from fastapi import APIRouter, Depends
from firebase_admin import auth

from app.core.security import get_current_user

router = APIRouter(prefix="/firebase",tags=["Firebase"])

@router.post("/token")
def get_firebase_token(current_user=Depends(get_current_user)):
    firebase_token = auth.create_custom_token(current_user.id)
    return {
        "firebase_token": firebase_token.decode("utf-8")
    }
