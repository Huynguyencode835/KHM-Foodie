from flask import Flask
from app.config import config_map


def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    from app.routes import register_routes
    register_routes(app)

    return app
