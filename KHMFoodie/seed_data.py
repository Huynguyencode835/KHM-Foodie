import json
import os
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.model import (
    User, Restaurant, Dish, Voucher, Order, OrderItem,
    UserRole, CuisineType, DishCategory, DiscountType, Status,
    RestaurantApprovalStatus, PaymentTransaction,
    hash_password, parse_time
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESTAURANTS_JSON = os.path.join(BASE_DIR, "app", "data", "restaurants.json")
DISHES_JSON = os.path.join(BASE_DIR, "app", "data", "dishes.json")


def seed(app=None):
    if app is None:
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

        _seed_orders(restaurant_map)
        _seed_orders_full_status(restaurant_map)

        print(f"✅ Đã tạo {len(restaurant_map)} nhà hàng và {len(dishes_data)} món ăn.")


def _seed_orders(restaurant_map):
    """Tạo đơn hàng test cho nhà hàng đã duyệt, trải đủ trạng thái, nhiều khách hàng khác nhau."""
    customer_specs = [
        ("Nguyen Van A", "khach_a", "0911000111", "khacha@example.com", "12 Le Loi, Q1, TP.HCM"),
        ("Tran Thi B", "khach_b", "0911000222", "khachb@example.com", "34 Nguyen Hue, Q3, TP.HCM"),
        ("Le Van C", "khach_c", "0911000333", "khachc@example.com", "56 Hai Ba Trung, Q7, TP.HCM"),
        ("Pham Thi D", "khach_d", "0911000444", "khachd@example.com", "78 Ly Thuong Kiet, Q10, TP.HCM"),
    ]

    customer_users = []
    for name, username, phone, email, addr in customer_specs:
        customer = User(
            name=name,
            username=username,
            password=hash_password("123456"),
            phonenumber=phone,
            email=email,
            address=addr,
            role=UserRole.CUSTOMER,
        )
        db.session.add(customer)
        customer_users.append(customer)
    db.session.flush()

    # Voucher mẫu cho nhà hàng test (quan_trua_ngon)
    rest_test = restaurant_map["quan_trua_ngon"]
    vouchers = [
        Voucher(
            name="Giam 10% toi da 50k",
            code="QUANTRUANGON10",
            description="Giam 10% don hang, toi da 50k",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=10,
            minimum_order=100,
            max_discount=50,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow() + timedelta(days=30),
            usage_limit=1000,
            used_count=5,
            restaurant_id=rest_test.id,
        ),
        Voucher(
            name="Giam 30k",
            code="QUANTRUANGON30",
            description="Giam 30k don hang tu 150k",
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_value=30,
            minimum_order=150,
            max_discount=None,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow() + timedelta(days=30),
            usage_limit=1000,
            used_count=3,
            restaurant_id=rest_test.id,
        ),
    ]
    db.session.add_all(vouchers)
    db.session.flush()

    # Đơn hàng cho 2 nhà hàng approved: quan_trua_ngon & goc_trua_van_phong
    # spec: (restaurant_username, status, customer_idx, ship_fee, voucher_idx, note, days_ago)
    order_specs = [
        ("quan_trua_ngon", Status.PAID, 0, 20, 0, "Giao gio hanh chinh", 0),
        ("quan_trua_ngon", Status.PAID, 1, 20, 1, None, 1),
        ("quan_trua_ngon", Status.PAID, 2, 15, None, "Them it tuong ot", 2),
        ("quan_trua_ngon", Status.PAID, 3, 25, 0, None, 3),
        ("quan_trua_ngon", Status.CONFIRMED, 1, 20, None, None, 1),
        ("quan_trua_ngon", Status.CONFIRMED, 2, 15, 1, "Giao trua 11h30", 2),
        ("quan_trua_ngon", Status.PREPARING, 0, 20, None, None, 0),
        ("quan_trua_ngon", Status.PREPARING, 3, 15, 0, None, 1),
        ("quan_trua_ngon", Status.DELIVERING, 2, 20, None, None, 0),
        ("quan_trua_ngon", Status.DELIVERING, 1, 25, 1, None, 2),
        ("quan_trua_ngon", Status.COMPLETED, 0, 20, None, None, 5),
        ("quan_trua_ngon", Status.CANCELLED, 3, 0, None, "Nha hang het nguyen lieu", 4),
        ("quan_trua_ngon", Status.PENDING_PAYMENT, 1, 20, None, None, 0),
        ("goc_trua_van_phong", Status.PAID, 2, 15, None, None, 1),
        ("goc_trua_van_phong", Status.CONFIRMED, 3, 20, None, None, 2),
        ("goc_trua_van_phong", Status.PREPARING, 0, 15, None, None, 0),
        ("goc_trua_van_phong", Status.DELIVERING, 1, 20, None, None, 1),
        ("goc_trua_van_phong", Status.COMPLETED, 2, 15, None, None, 6),
        ("goc_trua_van_phong", Status.CANCELLED, 3, 0, None, "Khach huy don", 3),
    ]

    orders_created = 0
    for username, status, cust_idx, ship_fee, voucher_idx, note, days_ago in order_specs:
        restaurant = restaurant_map[username]
        customer = customer_users[cust_idx]
        dishes = Dish.query.filter_by(restaurant_id=restaurant.id).order_by(Dish.id).all()
        if not dishes:
            continue

        voucher = vouchers[voucher_idx] if voucher_idx is not None else None
        chosen = dishes[:3]
        items = []
        subtotal = 0
        for i, dish in enumerate(chosen):
            qty = (i % 3) + 1
            unit_price = float(dish.price)
            subtotal += unit_price * qty
            items.append(OrderItem(name=dish.name, dish_id=dish.id, unit_price=unit_price, quantity=qty))

        discount = 0
        if voucher:
            if voucher.discount_type == DiscountType.PERCENTAGE:
                discount = subtotal * voucher.discount_value / 100
                if voucher.max_discount is not None:
                    discount = min(discount, voucher.max_discount)
            else:
                discount = min(voucher.discount_value, subtotal)
        total = subtotal - discount + ship_fee

        rejection_reason = note if status == Status.CANCELLED else None
        order = Order(
            name=f"DH-{orders_created + 1:05d}",
            user_id=customer.id,
            restaurant_id=restaurant.id,
            voucher_id=voucher.id if voucher else None,
            status=status,
            note=note,
            customer_name=customer.name,
            customer_phone=customer.phonenumber,
            customer_email=customer.email,
            delivery_address=customer.address,
            shipping_fee=ship_fee,
            total_amount=total,
            rejection_reason=rejection_reason,
            created_at=datetime.utcnow() - timedelta(days=days_ago),
        )
        order.items = items
        db.session.add(order)
        orders_created += 1

    db.session.commit()
    print(f"✅ Đã tạo {orders_created} đơn hàng test.")


def _seed_orders_full_status(restaurant_map):
    """Tạo 1 customer test riêng và đủ 8 trạng thái Order cho customer đó,
    kèm PaymentTransaction liên kết đúng theo từng trạng thái."""

    test_customer = User(
        name="Nguyen Van Test",
        username="khach_test",
        password=hash_password("123456"),
        phonenumber="0900000000",
        email="khachtest@example.com",
        address="99 Vo Van Tan, Q3, TP.HCM",
        role=UserRole.CUSTOMER,
    )
    db.session.add(test_customer)
    db.session.flush()

    rest_test = restaurant_map["quan_trua_ngon"]

    voucher = Voucher(
        name="Giam 10% toi da 50k",
        code="TESTVOUCHER10",
        description="Giam 10% don hang, toi da 50k",
        discount_type=DiscountType.PERCENTAGE,
        discount_value=10,
        minimum_order=100,
        max_discount=50,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow() + timedelta(days=30),
        usage_limit=1000,
        used_count=1,
        restaurant_id=rest_test.id,
    )
    db.session.add(voucher)
    db.session.flush()

    dishes = Dish.query.filter_by(restaurant_id=rest_test.id).order_by(Dish.id).all()
    if not dishes:
        print("⚠ Không có món ăn cho nhà hàng test, bỏ qua seed order đủ trạng thái.")
        return

    # spec: (status, ship_fee, dùng voucher?, note, rejection_reason, days_ago)
    order_specs = [
        (Status.PENDING_PAYMENT, 20, False, None, None, 0),
        (Status.PAYMENT_FAILED, 20, False, None, "Thanh toan that bai tu cong VNPAY", 0),
        (Status.PAID, 20, True, "Giao gio hanh chinh", None, 1),
        (Status.CONFIRMED, 15, False, "Giao truoc 12h", None, 2),
        (Status.PREPARING, 20, True, None, None, 1),
        (Status.DELIVERING, 25, False, None, None, 0),
        (Status.COMPLETED, 20, True, None, None, 5),
        (Status.CANCELLED, 0, False, "Khach doi y", "Khach huy don truoc khi xac nhan", 3),
    ]

    orders_created = 0
    for status, ship_fee, use_voucher, note, rejection_reason, days_ago in order_specs:
        chosen = dishes[:3]
        items = []
        subtotal = 0
        for i, dish in enumerate(chosen):
            qty = (i % 3) + 1
            unit_price = float(dish.price)
            subtotal += unit_price * qty
            items.append(OrderItem(name=dish.name, dish_id=dish.id, unit_price=unit_price, quantity=qty))

        discount = 0
        applied_voucher = voucher if use_voucher else None
        if applied_voucher:
            if applied_voucher.discount_type == DiscountType.PERCENTAGE:
                discount = subtotal * applied_voucher.discount_value / 100
                if applied_voucher.max_discount is not None:
                    discount = min(discount, applied_voucher.max_discount)
            else:
                discount = min(applied_voucher.discount_value, subtotal)

        total = subtotal - discount + ship_fee

        order = Order(
            name=f"DH-TEST-{orders_created + 1:03d}",
            user_id=test_customer.id,
            restaurant_id=rest_test.id,
            voucher_id=applied_voucher.id if applied_voucher else None,
            status=status,
            note=note,
            customer_name=test_customer.name,
            customer_phone=test_customer.phonenumber,
            customer_email=test_customer.email,
            delivery_address=test_customer.address,
            shipping_fee=ship_fee,
            total_amount=total,
            rejection_reason=rejection_reason,
            created_at=datetime.utcnow() - timedelta(days=days_ago),
        )
        order.items = items
        db.session.add(order)
        db.session.flush()  # cần order.id trước khi tạo payment_transaction

        txn_name = f"Giao dich {order.name}"

        if status == Status.PENDING_PAYMENT:
            db.session.add(PaymentTransaction(
                name=txn_name,
                order_id=order.id,
                gateway="VNPAY",
                vnp_txn_ref=f"TXNREF-TEST-{orders_created + 1:03d}-1",
                amount=total,
                status="CREATED",
                ip_addr="127.0.0.1",
                payment_url="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?...",
            ))
        elif status == Status.PAYMENT_FAILED:
            db.session.add(PaymentTransaction(
                name=txn_name,
                order_id=order.id,
                gateway="VNPAY",
                vnp_txn_ref=f"TXNREF-TEST-{orders_created + 1:03d}-1",
                amount=total,
                status="FAILED",
                ip_addr="127.0.0.1",
                vnp_response_code="24",
                vnp_transaction_status="02",
                completed_at=datetime.utcnow() - timedelta(days=days_ago),
            ))
        elif status in (
            Status.PAID, Status.CONFIRMED, Status.PREPARING,
            Status.DELIVERING, Status.COMPLETED,
        ):
            db.session.add(PaymentTransaction(
                name=txn_name,
                order_id=order.id,
                gateway="VNPAY",
                vnp_txn_ref=f"TXNREF-TEST-{orders_created + 1:03d}-1",
                amount=total,
                status="SUCCESS",
                ip_addr="127.0.0.1",
                vnp_transaction_no=f"14{orders_created + 1:06d}",
                vnp_response_code="00",
                vnp_transaction_status="00",
                bank_code="NCB",
                pay_date=(datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y%m%d%H%M%S"),
                completed_at=datetime.utcnow() - timedelta(days=days_ago),
            ))
        # CANCELLED (huỷ trước khi xác nhận): không tạo payment_transaction

        orders_created += 1

    db.session.commit()
    print(f"✅ Đã tạo user '{test_customer.username}' và {orders_created} đơn hàng đủ 8 trạng thái.")


if __name__ == "__main__":
    seed()