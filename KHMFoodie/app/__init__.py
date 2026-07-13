import os
from flask import Flask
from app.config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from app.extensions import db
import cloudinary


load_dotenv()
oauth = OAuth()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from app.models.model import User
    return User.query.get(int(user_id))



cloudinary.config(
    cloud_name= os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


def create_app(config_name='dev'):
    app = Flask(__name__)

    app.config.from_object(config_map[config_name])

    login_manager.init_app(app)
    db.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id= os.getenv('CLIENT_ID_GOOGLE'),
        client_secret=os.getenv('CLIENT_SECRET_GOOGLE'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    from app.routes import register_routes
    register_routes(app)
    from app.routes.routes_API.index import route_api
    route_api(app)

    return app




