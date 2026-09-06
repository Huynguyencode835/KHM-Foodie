from flask_migrate import Migrate
import json
import base64
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from flask_mail import Mail
from firebase_admin import credentials, firestore, auth as fb_auth

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
firestore_db = None

def init_firebase(app):
    global firestore_db
    if not firebase_admin._apps:
        cred_b64 = app.config['FIREBASE_CREDENTIALS_BASE64']
        cred_json = json.loads(base64.b64decode(cred_b64).decode('utf-8'))
        cred = credentials.Certificate(cred_json)
        firebase_admin.initialize_app(cred)

    firestore_db = firestore.client()

def mint_firebase_custom_token(user_id):
    """user_id là int từ SQLAlchemy (User.id) -> ép về string vì Firebase
    uid luôn là string."""
    uid = str(user_id)
    return fb_auth.create_custom_token(uid).decode('utf-8')