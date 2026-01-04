from firebase_admin import messaging
from app.db.database import db


def send_incoming_call_notification(
    callee_user_id: str,
    call_id: str,
    caller_name: str
):
    user = db.users.find_one({"_id": callee_user_id})

    if not user or "fcm_token" not in user:
        return False

    message = messaging.Message(
        data={
            "type": "incoming_call",
            "call_id": call_id,
            "caller_name": caller_name
        },
        token=user["fcm_token"],
        android=messaging.AndroidConfig(
            priority="high"
        )
    )

    messaging.send(message)
    return True
