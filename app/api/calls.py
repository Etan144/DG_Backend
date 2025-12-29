from fastapi import APIRouter,HTTPException
from uuid import uuid4
from datetime import datetime

from app.schemas.call_signalling import (
    InviteRequest,
    OfferRequest,
    AnswerRequest,
    IceCandidateRequest
)

from app.services.call_store import CALL_SESSIONS

router = APIRouter()

@router.post("/calls/invite")
def invite(data: InviteRequest):
    call_id = str(uuid4())

    CALL_SESSIONS[call_id] = {
        "call_id": call_id,
        "caller_user_id": "caller_id_placeholder",  # from JWT later
        "callee_user_id": data.callee_user_id,
        "status": "ringing",
        "offer": None,
        "answer": None,
        "ice": {
            "caller": [],
            "callee": []
        },
        "created_at": datetime.utcnow()
    }

    return {"call_id": call_id}

@router.post("/calls/{call_id}/offer")
def offer(call_id: str, data: OfferRequest):
    session = CALL_SESSIONS.get(call_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call not found")

    session["offer"] = data.sdp
    session["status"] = "accepted"

    return {"message": "Offer received"}

@router.post("/calls/{call_id}/answer")
def answer(call_id: str, data: AnswerRequest):
    session = CALL_SESSIONS.get(call_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call not found")

    session["answer"] = data.sdp
    session["status"] = "in_call"

    return {"message": "Answer received"}

@router.post("/calls/{call_id}/ice")
def ice(call_id: str, data: IceCandidateRequest, role: str):
    session = CALL_SESSIONS.get(call_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call not found")

    if role not in ["caller", "callee"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    session["ice"][role].append(data.dict())

    return {"message": "ICE candidate added"}

@router.get("/calls/{call_id}/events")
def events(call_id: str):
    session = CALL_SESSIONS.get(call_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "status": session["status"],
        "offer": session["offer"],
        "answer": session["answer"],
        "ice": session["ice"]
    }