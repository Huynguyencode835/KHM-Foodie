from flask import request, jsonify, redirect
from app.models.model import hash_password
from app.dao.userDao import add_user
from app.dao.userDao import UserDao
from flask_login import login_user, logout_user, login_required, current_user


class LoginController:

    @staticmethod
    def login():
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid JSON"}), 400

        username = data.get("username")
        password = data.get("password")
        remember = data.get("remember", False)

        if not username or not password:
            return jsonify({"message": "Username and password required"}), 400

        user = UserDao.get_by_username(username)
        if user and user.password == hash_password(password):
            login_user(user, remember=remember)
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role.value if user.role else None
                }
            }), 200

        return jsonify({"message": "Invalid credentials"}), 401

    @staticmethod
    def logout():
        logout_user()
        return redirect('/')

    @staticmethod
    @login_required
    def update_profile():
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid JSON"}), 400

        allowed_fields = ['name', 'phonenumber', 'email', 'address', 'avatar', 'description', 'cover_image', 'cuisine_type', 'opening_time', 'closing_time', 'tax_code', 'status']
        update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        if not update_data:
            return jsonify({"message": "No valid fields to update"}), 400

        user = UserDao.update_profile(current_user.id, update_data)
        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phonenumber": user.phonenumber,
                "address": user.address,
                "avatar": user.avatar,
                "role": user.role.value if user.role else None
            }
        }), 200


# def add_user(
#     name,
#     phonenumber=None,
#     username=None,
#     password=None,
#     email=None,
#     role=None,
#     is_restaurant=False,
#     **kwargs
# ):
    @staticmethod
    def register():
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid JSON"}), 400

        name = data.get("name")
        username = data.get("username")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not all([name, username, email, phone, password, confirm_password]):
            return jsonify({"message": "All fields are required"}), 400

        if password != confirm_password:
            return jsonify({"message": "Passwords do not match"}), 400

        if UserDao.get_by_username(username):
            return jsonify({"message": "Username already exists"}), 409

        add_user(name, phone, username, password, email)
        return jsonify({"message": "Registration successful"}), 201
