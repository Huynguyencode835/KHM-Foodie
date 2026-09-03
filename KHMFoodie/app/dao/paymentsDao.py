from decimal import Decimal
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.model import PaymentTransaction, Order


class PaymentDao:
    STATUS_CREATED = "CREATED"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    TERMINAL_STATUSES = {
        STATUS_SUCCESS,
        STATUS_FAILED,
    }

    @staticmethod
    def _to_decimal(value):
        if value is None:
            return Decimal("0")
        return Decimal(str(value))

    @staticmethod
    def create_transaction(order_id, txn_ref, amount):
        if not txn_ref:
            raise ValueError("txn_ref là bắt buộc")

        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order không tồn tại")

        existing = PaymentTransaction.query.filter_by(
            vnp_txn_ref=txn_ref
        ).first()

        if existing:
            return existing

        transaction = PaymentTransaction(
            name=f"vnpay-{txn_ref}",
            order_id=order_id,
            gateway="VNPAY",
            vnp_txn_ref=txn_ref,
            amount=PaymentDao._to_decimal(amount),
            status=PaymentDao.STATUS_CREATED,
        )

        try:
            db.session.add(transaction)
            db.session.commit()
            return transaction

        except IntegrityError:
            db.session.rollback()
            return PaymentTransaction.query.filter_by(
                vnp_txn_ref=txn_ref
            ).first()

        except Exception:
            db.session.rollback()
            raise


    @staticmethod
    def get_transaction_by_txn_ref(txn_ref):
        if not txn_ref:
            return None

        return PaymentTransaction.query.options(
            db.joinedload(PaymentTransaction.order)
        ).filter_by(
            vnp_txn_ref=txn_ref
        ).first()


    @staticmethod
    def mark_transaction_result(
        txn_ref,
        response_code,
        transaction_no,
        bank_code,
        pay_date
    ):
        if not txn_ref:
            raise ValueError("txn_ref là bắt buộc")

        try:
            transaction = PaymentTransaction.query.filter_by(
                vnp_txn_ref=txn_ref
            ).with_for_update().first()

            if not transaction:
                return None, False

            if transaction.status in PaymentDao.TERMINAL_STATUSES:
                return transaction, False

            new_status = (
                PaymentDao.STATUS_SUCCESS
                if response_code == "00"
                else PaymentDao.STATUS_FAILED
            )

            transaction.status = new_status
            transaction.vnp_response_code = response_code
            transaction.vnp_transaction_no = transaction_no
            transaction.bank_code = bank_code
            transaction.pay_date = pay_date
            transaction.completed_at = datetime.utcnow()

            db.session.commit()
            return transaction, True

        except Exception:
            db.session.rollback()
            raise