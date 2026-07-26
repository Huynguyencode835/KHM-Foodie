from datetime import datetime
from flask import request, jsonify, abort
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.model import Voucher, DiscountType, UserRole
from app.dao.vouchersDao import VouchersDao


class VoucherController:
    @staticmethod
    def _require_restaurant():
        if current_user.role != UserRole.RESTAURANT:
            abort(403)

        restaurant = current_user.restaurant
        if not restaurant:
            abort(403)

        return restaurant.id

    @staticmethod
    def _serialize_voucher(voucher):
        return {
            "id": voucher.id,
            "name": voucher.name,
            "code": voucher.code,
            "description": voucher.description,
            "discount_type": voucher.discount_type.name if voucher.discount_type else None,
            "discount_value": voucher.discount_value,
            "minimum_order": voucher.minimum_order,
            "max_discount": voucher.max_discount,
            "start_date": voucher.start_date.isoformat() if voucher.start_date else None,
            "end_date": voucher.end_date.isoformat() if voucher.end_date else None,
            "usage_limit": voucher.usage_limit,
            "used_count": voucher.used_count,
            "restaurant_id": voucher.restaurant_id,
            "active": voucher.active,
            "created_at": voucher.created_at.isoformat() if voucher.created_at else None,
            "created_updated_at": voucher.created_updated_at.isoformat() if voucher.created_updated_at else None,
        }

    @staticmethod
    def _parse_datetime(value, field_name):
        if not value:
            raise ValueError(f"{field_name} là bắt buộc")

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"{field_name} không đúng định dạng datetime")

    @staticmethod
    def _parse_discount_type(value):
        if not value:
            raise ValueError("discount_type là bắt buộc")

        try:
            return DiscountType[value]
        except KeyError:
            raise ValueError("discount_type không hợp lệ")

    @staticmethod
    def _validate_payload(data, is_update=False):
        if not data:
            return None, {"message": "Invalid JSON"}

        cleaned = {}
        errors = {}

        allowed_fields = {
            "name", "code", "description", "discount_type", "discount_value",
            "minimum_order", "max_discount", "start_date", "end_date", "usage_limit"
        }

        for key in data:
            if key not in allowed_fields:
                continue
            cleaned[key] = data.get(key)

        required_fields = ["name", "code", "discount_type", "discount_value", "start_date", "end_date", "usage_limit"]
        if not is_update:
            for field in required_fields:
                if cleaned.get(field) in [None, ""]:
                    errors[field] = f"{field} là bắt buộc"

        if "name" in cleaned and cleaned["name"] is not None:
            cleaned["name"] = str(cleaned["name"]).strip()
            if not cleaned["name"]:
                errors["name"] = "Tên voucher không được để trống"

        if "code" in cleaned and cleaned["code"] is not None:
            cleaned["code"] = str(cleaned["code"]).strip().upper()
            if not cleaned["code"]:
                errors["code"] = "Mã voucher không được để trống"

        if "description" in cleaned and cleaned["description"] is not None:
            cleaned["description"] = str(cleaned["description"]).strip()

        if "discount_type" in cleaned and cleaned["discount_type"] is not None:
            try:
                cleaned["discount_type"] = VoucherController._parse_discount_type(cleaned["discount_type"])
            except ValueError as e:
                errors["discount_type"] = str(e)

        number_fields = ["discount_value", "minimum_order", "max_discount", "usage_limit"]
        for field in number_fields:
            if field in cleaned and cleaned[field] not in [None, ""]:
                try:
                    if field == "usage_limit":
                        cleaned[field] = int(cleaned[field])
                    else:
                        cleaned[field] = float(cleaned[field])
                except (TypeError, ValueError):
                    errors[field] = f"{field} phải là số hợp lệ"

        if "discount_value" in cleaned and isinstance(cleaned.get("discount_value"), (int, float)):
            if cleaned["discount_value"] <= 0:
                errors["discount_value"] = "discount_value phải lớn hơn 0"

        if "minimum_order" in cleaned and isinstance(cleaned.get("minimum_order"), (int, float)):
            if cleaned["minimum_order"] < 0:
                errors["minimum_order"] = "minimum_order không được âm"

        if "usage_limit" in cleaned and isinstance(cleaned.get("usage_limit"), int):
            if cleaned["usage_limit"] < 1:
                errors["usage_limit"] = "usage_limit phải >= 1"

        if "start_date" in cleaned and cleaned["start_date"] not in [None, ""]:
            try:
                cleaned["start_date"] = VoucherController._parse_datetime(cleaned["start_date"], "start_date")
            except ValueError as e:
                errors["start_date"] = str(e)

        if "end_date" in cleaned and cleaned["end_date"] not in [None, ""]:
            try:
                cleaned["end_date"] = VoucherController._parse_datetime(cleaned["end_date"], "end_date")
            except ValueError as e:
                errors["end_date"] = str(e)

        if (
            "start_date" in cleaned and "end_date" in cleaned
            and isinstance(cleaned.get("start_date"), datetime)
            and isinstance(cleaned.get("end_date"), datetime)
        ):
            if cleaned["start_date"] >= cleaned["end_date"]:
                errors["end_date"] = "end_date phải lớn hơn start_date"

        discount_type = cleaned.get("discount_type")
        discount_value = cleaned.get("discount_value")

        if discount_type == DiscountType.PERCENTAGE and isinstance(discount_value, (int, float)):
            if discount_value > 100:
                errors["discount_value"] = "Voucher phần trăm không được vượt quá 100"

        if discount_type == DiscountType.FIXED_AMOUNT:
            cleaned["max_discount"] = None

        if errors:
            return None, {"message": "Dữ liệu không hợp lệ", "errors": errors}

        return cleaned, None

    @staticmethod
    @login_required
    def list_vouchers():
        restaurant_id = VoucherController._require_restaurant()
        vouchers = VouchersDao.get_all_by_restaurant(restaurant_id)

        return jsonify({
            "items": [VoucherController._serialize_voucher(v) for v in vouchers]
        }), 200

    @staticmethod
    @login_required
    def create_voucher():
        restaurant_id = VoucherController._require_restaurant()

        data = request.get_json()
        payload, error = VoucherController._validate_payload(data, is_update=False)
        if error:
            return jsonify(error), 400

        try:
            voucher = Voucher(
                name=payload["name"],
                code=payload["code"],
                description=payload.get("description"),
                discount_type=payload["discount_type"],
                discount_value=payload["discount_value"],
                minimum_order=payload.get("minimum_order", 0),
                max_discount=payload.get("max_discount"),
                start_date=payload["start_date"],
                end_date=payload["end_date"],
                usage_limit=payload["usage_limit"],
                restaurant_id=restaurant_id
            )

            voucher = VouchersDao.create_voucher(voucher)

            return jsonify({
                "message": "Tạo voucher thành công",
                "voucher": VoucherController._serialize_voucher(voucher)
            }), 201

        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "message": "Mã voucher đã tồn tại"
            }), 409

    @staticmethod
    @login_required
    def update_voucher(voucher_id):
        restaurant_id = VoucherController._require_restaurant()

        voucher = VouchersDao.get_by_id_and_restaurant(voucher_id, restaurant_id)
        if not voucher:
            return jsonify({"message": "Voucher không tồn tại"}), 404

        data = request.get_json()
        payload, error = VoucherController._validate_payload(data, is_update=True)
        if error:
            return jsonify(error), 400

        try:
            for key, value in payload.items():
                setattr(voucher, key, value)

            voucher = VouchersDao.save(voucher)

            return jsonify({
                "message": "Cập nhật voucher thành công",
                "voucher": VoucherController._serialize_voucher(voucher)
            }), 200

        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "message": "Mã voucher đã tồn tại"
            }), 409

    @staticmethod
    @login_required
    def delete_voucher(voucher_id):
        restaurant_id = VoucherController._require_restaurant()

        voucher = VouchersDao.get_by_id_and_restaurant(voucher_id, restaurant_id)
        if not voucher:
            return jsonify({"message": "Voucher không tồn tại"}), 404

        VouchersDao.soft_delete(voucher)

        return jsonify({
            "message": "Xóa voucher thành công"
        }), 200