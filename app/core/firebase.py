import os,json,base64
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    if not os.getenv("FIREBASE_CREDENTIALS_B64"):
        raise RuntimeError("FIREBASE_CREDENTIALS_B64 not set")

    if not firebase_admin._apps:
        cred_dict = json.loads(
            base64.b64decode(os.getenv("FIREBASE_CREDENTIALS_B64"))
        )
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()

firestore_db = init_firebase()