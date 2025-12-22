from fastapi import APIRouter, Depends
from app.core.security import get_current_user

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
        "username": current_user["username"]
    }