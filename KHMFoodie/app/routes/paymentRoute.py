from flask import Blueprint, render_template

payment_bp = Blueprint("payment_bp", __name__)


@payment_bp.route("/payment")
def payment():
    return render_template("payment.html")
