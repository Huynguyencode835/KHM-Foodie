from flask import Blueprint

from app.controllers.notificationController import NotificationController

notification_bp = Blueprint('notification_bp', __name__)

notification_bp.add_url_rule('/', view_func=NotificationController.index)
