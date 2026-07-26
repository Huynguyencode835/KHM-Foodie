from flask import render_template


class NotificationController:
    @staticmethod
    def index():
        return render_template(
            "notification.html",
            title="Chi tiết nhà hàng"
        )