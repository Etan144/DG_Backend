from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from datetime import datetime

from app.schemas.call_signalling import InviteRequest
from app.core.firebase import firestore_db
from app.core.security import get_current_user

router = APIRouter(prefix="/calls",tags=["Calls"])

@router.post("/invite")
def invite(data: InviteRequest, current_user=Depends(get_current_user)):
    call_id = str(uuid4())

    firestore_db.collection("calls").document(call_id).set({
        "call_id":call_id,
        "caller_user_id": current_user.id,
        "callee_user_id": data.callee_user_id,
        "status":"ringing",
        "created_at": datetime.utcnow()
    })

    return {"call_id": call_id}

@router.post("/{call_id}/end")
def end_call(call_id:str, current_user=Depends(get_current_user)):
    doc_ref = firestore_db.collection("calls").document(call_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Call not found")
    
    data = doc.to_dict()

    #Auth check
    if current_user.id not in [data["caller_user_id"],data["callee_user_id"]]:
        raise HTTPException(status_code=403,detail="Not authorized to end this call")
    
    doc_ref.update({
        "status":"ended",
        "ended_at": datetime.utcnow()
    })

    return {"message":"Call ended"}