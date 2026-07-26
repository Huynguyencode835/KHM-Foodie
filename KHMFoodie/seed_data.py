import json
import os
from app import create_app
from app.extensions import db
from app.models.model import (
    User, Restaurant, Dish,
    UserRole, CuisineType, DishCategory,
    RestaurantApprovalStatus,
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

        if User.query.first():
            print("ℹ Data already exists, skipping seed.")
            return

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
            new_user = User(
                name=r["name"],
                username=r["username"],
                password=hash_password(r["password"]),
                phonenumber=r.get("phonenumber"),
                email=r.get("email"),
                address=r.get("address"),
                avatar=r.get("avatar"),
                role=UserRole.RESTAURANT
            )
            db.session.add(new_user)
            db.session.flush()

            new_restaurant = Restaurant(
                id=new_user.id,
                name=r["name"],
                cover_image=r.get("cover_image"),
                description=r.get("description"),
                status=r.get("status", True),
                opening_time=parse_time(r.get("opening_time")),
                closing_time=parse_time(r.get("closing_time")),
                cuisine_type=CuisineType[r["cuisine_type"]] if r.get("cuisine_type") else None,
                tax_code=r.get("tax_code"),
                approval_status=RestaurantApprovalStatus.APPROVED,
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

        # ---------- 5 nhà hàng PENDING để test duyệt ----------
        pending_restaurants = [
            ("Bún Bò Huế Cô Ba", "bunbohue", "123456", "Huế", CuisineType.VIETNAMESE, "06:00", "22:00"),
            ("Lẩu Cua Đồng Út Tịch", "laucua", "123456", "Cần Thơ", CuisineType.VIETNAMESE, "10:00", "23:00"),
            ("Ốc Đào Cô Liên", "ocddao", "123456", "Sài Gòn", CuisineType.SEAFOOD, "11:00", "23:00"),
            ("Cháo Lòng Bà Điệp", "chaolong", "123456", "Hà Nội", CuisineType.VIETNAMESE, "06:00", "14:00"),
            ("Cơm Niêu Đệ Nhất", "comnieu", "123456", "Nha Trang", CuisineType.VIETNAMESE, "10:00", "21:00"),
        ]

        for name, username, pw, addr, ctype, open_t, close_t in pending_restaurants:
            new_user = User(
                name=name,
                username=username,
                password=hash_password(pw),
                email=f"{username}@email.com",
                address=addr,
                role=UserRole.RESTAURANT,
                active=False,
            )
            db.session.add(new_user)
            db.session.flush()

            new_restaurant = Restaurant(
                id=new_user.id,
                name=name,
                active=False,
                approval_status=RestaurantApprovalStatus.PENDING,
                cuisine_type=ctype,
                opening_time=parse_time(open_t),
                closing_time=parse_time(close_t),
            )
            db.session.add(new_restaurant)

        db.session.commit()
        print(f"✅ Thêm {len(pending_restaurants)} nhà hàng chờ duyệt.")

        print(f"✅ Đã tạo {len(restaurant_map)} nhà hàng và {len(dishes_data)} món ăn.")


if __name__ == "__main__":
    seed()