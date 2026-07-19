import json
import os
from app import create_app
from app.extensions import db
from app.models.model import (
    User, Restaurant, Dish,
    UserRole, CuisineType, DishCategory,
    hash_password, parse_time
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESTAURANTS_JSON = os.path.join(BASE_DIR, "app", "data", "restaurants.json")
DISHES_JSON = os.path.join(BASE_DIR, "app", "data", "dishes.json")


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ---------- Admin & Customer mẫu ----------
        # Admin: username=admin, password=123456
        new_admin = User(
            name="Quản trị viên",
            username="admin",
            role = UserRole.ADMIN,
            password=hash_password("123456"),
            avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfjno7hGrNNuPZwaFZ8U8Mhr_Yq39rzd_p0YN_HVYk6KFmMETjtgd9bwl0UhU6g4xDDGg&usqp=CAU",
        )

        new_customer = User(
            name="Customer",
            username="customer",
            password=hash_password("customer"),
            avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfjno7hGrNNuPZwaFZ8U8Mhr_Yq39rzd_p0YN_HVYk6KFmMETjtgd9bwl0UhU6g4xDDGg&usqp=CAU",
            role=UserRole.CUSTOMER
        )

        db.session.add_all([new_admin, new_customer])
        db.session.commit()

        # ---------- Đọc dữ liệu nhà hàng từ JSON ----------
        with open(RESTAURANTS_JSON, "r", encoding="utf-8") as f:
            restaurants_data = json.load(f)

        restaurant_map = {}

        for r in restaurants_data:
            new_restaurant = Restaurant(
                name=r["name"],
                username=r["username"],
                password=hash_password(r["password"]),
                phonenumber=r.get("phonenumber"),
                email=r.get("email"),
                address=r.get("address"),
                avatar=r.get("avatar"),
                cover_image=r.get("cover_image"),
                description=r.get("description"),
                status=r.get("status", True),
                opening_time=parse_time(r.get("opening_time")),
                closing_time=parse_time(r.get("closing_time")),
                cuisine_type=CuisineType[r["cuisine_type"]] if r.get("cuisine_type") else None,
                tax_code=r.get("tax_code"),
                role=UserRole.RESTAURANT
            )
            db.session.add(new_restaurant)
            restaurant_map[r["username"]] = new_restaurant

        db.session.commit()

        # ---------- Đọc dữ liệu món ăn từ JSON ----------
        with open(DISHES_JSON, "r", encoding="utf-8") as f:
            dishes_data = json.load(f)

        for d in dishes_data:
            restaurant_obj = restaurant_map.get(d["restaurant_username"])
            if not restaurant_obj:
                continue

            new_dish = Dish(
                name=d["name"],
                description=d.get("description"),
                image=d.get("image"),
                price=d["price"],
                category=DishCategory[d["category"]],
                restaurant=restaurant_obj
            )
            db.session.add(new_dish)

        db.session.commit()

        print(f"✅ Đã tạo {len(restaurant_map)} nhà hàng và {len(dishes_data)} món ăn.")


if __name__ == "__main__":
    seed()