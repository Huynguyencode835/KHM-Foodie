from app.extensions import db
from app.models.model import Voucher, VoucherDish


class VouchersDao:
    @staticmethod
    def get_all_by_restaurant(restaurant_id):
        return Voucher.query.filter_by(
            restaurant_id=restaurant_id,
            active=True
        ).order_by(Voucher.created_at.desc()).all()

    @staticmethod
    def get_by_id_and_restaurant(voucher_id, restaurant_id):
        return Voucher.query.filter_by(
            id=voucher_id,
            restaurant_id=restaurant_id,
            active=True
        ).first()

    @staticmethod
    def get_dish_conflicts(dish_ids, restaurant_id, exclude_voucher_id=None):
        """Trả về {dish_id: voucher} cho các món đã thuộc một voucher khác đang hiệu lực."""
        if not dish_ids:
            return {}

        query = VoucherDish.query.join(Voucher).filter(
            VoucherDish.dish_id.in_(dish_ids),
            Voucher.restaurant_id == restaurant_id,
        )
        if exclude_voucher_id is not None:
            query = query.filter(Voucher.id != exclude_voucher_id)

        conflicts = {}
        for link in query.all():
            if link.voucher.is_valid_now():
                conflicts[link.dish_id] = link.voucher
        return conflicts

    @staticmethod
    def create_voucher(voucher, dishes):
        db.session.add(voucher)
        db.session.flush()
        VouchersDao.replace_dishes(voucher, dishes)
        db.session.commit()
        return voucher

    @staticmethod
    def save(voucher):
        db.session.commit()
        return voucher

    @staticmethod
    def replace_dishes(voucher, dishes):
        voucher.dish_links = [
            VoucherDish(voucher=voucher, dish=dish)
            for dish in dishes
        ]

    @staticmethod
    def soft_delete(voucher):
        voucher.active = False
        db.session.commit()
        return voucher
