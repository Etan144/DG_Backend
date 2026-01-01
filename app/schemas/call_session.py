from pydantic import BaseModel, Field, field_validator
from typing import List,Dict, Optional
from enum import Enum
from datetime import datetime

class CallStatus(str,Enum):
    ringing = "ringing"
    accepted = "accepted"
    on_hold = "on_hold"
    in_call = "in_call"
    ended = "ended"

class IceCandidate(BaseModel):
    candidate : str
    sdpMid : Optional[str]
    sdpMLineIndex : Optional[str]

class CallSession(BaseModel):
    call_id : str
    caller_user_id: str
    callee_user_id: str
    status : CallStatus
    

    offer_sdp : Optional[str] = None
    answer_sdp : Optional[str] = None

    #Store ICE candidates per user
    ice_candidates: Dict[str,List[IceCandidate]] = Field(default_factory=dict)

    created_at :datetime