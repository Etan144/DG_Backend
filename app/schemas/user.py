from pydantic import BaseModel

class FCMTokenRequest(BaseModel):
    fcm_token: str