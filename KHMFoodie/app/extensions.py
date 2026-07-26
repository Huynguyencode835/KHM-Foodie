from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from flask_mail import Mail
from firebase_admin import credentials, firestore

db = SQLAlchemy()
mail = Mail() 
firestore_db = None

def init_firebase(app):
    global firestore_db
    if not firebase_admin._apps:
        cred_path = app.config['FIREBASE_CREDENTIALS_PATH']
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    firestore_db = firestore.client()
