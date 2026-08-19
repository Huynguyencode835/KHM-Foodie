from flask import render_template, request, jsonify
from app.dao import dishesDao
from flask_login import current_user
import cloudinary.uploader


class RestaurantMenuController:

    @staticmethod
    def create_dishes():
        name = request.form.get("name")
        price = request.form.get("price")
        category = request.form.get("category")
        description = request.form.get("description")
        avatar_file = request.files.get("image")

        required_fields = {"name": name, "price": price, "category": category, "description": description}
        missing_fields = [key for key, value in required_fields.items() if value in [None, ""]]

        if missing_fields:
            return jsonify({
                "message": "Thiếu thông tin bắt buộc",
                "missing_fields": missing_fields
            }), 400

        image_url = None
        if avatar_file and avatar_file.filename:
            try:
                res = cloudinary.uploader.upload(avatar_file)
                image_url = res["secure_url"]
            except Exception as e:
                return jsonify({"message": "Upload ảnh thất bại", "error": str(e)}), 400

        try:
            new_dish = dishesDao.create_dishes(
                name=name,
                price=float(price),
                category=category,
                restaurant_id=current_user.id,
                description=description,
                image=image_url
            )

            if not new_dish:
                return jsonify({"message": "Tạo món ăn thất bại"}), 400

            return jsonify({"message": "successful"}), 200

        except ValueError as ve:
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            return jsonify({"message": "Lỗi hệ thống", "error": str(e)}), 500

    @staticmethod
    def index():
        return render_template(
            "retaurantMenuPage.html",
            title="Quản lý thực đơn"
        )