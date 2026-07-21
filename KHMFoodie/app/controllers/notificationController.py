from flask import jsonify, render_template, request


class NotificationController:
    @staticmethod
    def index():
        return render_template(
            "notification.html",
            title="Chi tiết nhà hàng"
        )