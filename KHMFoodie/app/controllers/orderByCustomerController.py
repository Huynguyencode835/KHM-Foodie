from flask import render_template, jsonify
from app.dao.ordersDao import OrdersDao

class OrderByCustomerController:

    @staticmethod
    def loadOrders():
        try:
            data = OrdersDao.get_orders_customer()
            return jsonify({
                "success": True,
                "data": data
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
        
    @staticmethod
    def get_order_detail_customer(order_id):
        data = OrdersDao.get_order_by_id_and_customer(order_id)
        if not data:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy đơn hàng"
            }), 404

        return jsonify({
            "success": True,
            "data": data
        }), 200
        
    @staticmethod
    def index():
        return render_template("orderByCustomer.html")

    @staticmethod
    def order_detail_page(order_id):
        return render_template("orderByCustomerDetail.html", order_id=order_id)