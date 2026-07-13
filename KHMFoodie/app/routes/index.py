from flask import Blueprint
from app.routes.searchRoute import search_bp
from app.routes.test import test_bp


def route_web(app):
    app.register_blueprint(test_bp, url_prefix='/')
    app.register_blueprint(search_bp, url_prefix='/search_customer')
