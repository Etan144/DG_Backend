from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.security import decode_access_token
from app.db.database import db
from app.schemas.user import FCMTokenRequest

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)] 
)

@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "username": current_user["username"],
        "display_name": current_user["username"],  
        "role": current_user["role"],               
        "plan_tier": current_user.get("plan_tier", "free"),
        "verified": current_user.get("verified", False),
        "created_at_seconds": int(current_user["created_at"].timestamp())
    }


@router.post("/fcm-token")
def register_fcm_token(request: FCMTokenRequest, current_user=Depends(get_current_user)):
    db.users.update_one( 
        {"_id": current_user["_id"]},
        {"$set":{"fcm_token": request.fcm_token}}
        )
    return {"status": "FCM token registered"}