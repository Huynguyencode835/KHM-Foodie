from app.routes.homeRoute import home_bp
from app.routes.loginRoute import login_bp
from app.routes.registerRoute import register_bp
from flask import Blueprint
from app.routes.searchRoute import search_bp
from app.routes.logInSignInGoogleRoute import google_auth_bp


def route_web(app):
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(login_bp, url_prefix='/')
    app.register_blueprint(register_bp, url_prefix='/')
    app.register_blueprint(google_auth_bp, url_prefix='/auth')
    app.register_blueprint(search_bp, url_prefix='/search_customer')