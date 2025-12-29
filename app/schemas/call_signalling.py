from pydantic import BaseModel
from typing import Optional, List

class InviteRequest(BaseModel):
    callee_user_id: str

class OfferRequest(BaseModel):
    sdp: str

class AnswerRequest(BaseModel):
    sdp : str

class IceCandidateRequest(BaseModel):
    candidate: str
    sdpMid: Optional[str]= None
    sdpMLineIndex: Optional[str] = None