from flask import Blueprint
from app.routes.test import test_bp
from app.routes.logInSignInGoogleRoute import google_auth_bp


def route_web(app):
    app.register_blueprint(test_bp, url_prefix='/')
    app.register_blueprint(google_auth_bp, url_prefix='/auth')
