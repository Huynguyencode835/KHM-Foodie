from flask import render_template, redirect, url_for
from flask_login import current_user
from app.models.model import UserRole


class NotificationController:
    @staticmethod
    def index():
        if current_user.is_authenticated:
            if current_user.role == UserRole.ADMIN:
                return redirect('/admin/')
            elif current_user.role == UserRole.RESTAURANT:
                return redirect(url_for('me_bp.me_page'))

        return render_template(
            "notification.html",
            title="Thông báo"
        )