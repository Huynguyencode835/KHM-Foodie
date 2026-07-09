from flask import Blueprint
from app.routes.test import test_bp


def route_web(app):
    app.register_blueprint(test_bp, url_prefix='/')
