import os
import hmac
import hashlib
import re
import unicodedata
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

VN_TZ = timezone(timedelta(hours=7))

VNP_RESPONSE_MESSAGES = {
    "00": "Giao dịch thành công",
    "07": "Trừ tiền thành công nhưng giao dịch bị nghi ngờ gian lận",
    "09": "Thẻ/Tài khoản chưa đăng ký Internet Banking",
    "10": "Xác thực thông tin thẻ/tài khoản không đúng quá 3 lần",
    "11": "Đã hết hạn chờ thanh toán",
    "12": "Thẻ/Tài khoản bị khóa",
    "13": "Nhập sai mật khẩu xác thực giao dịch OTP",
    "24": "Khách hàng hủy giao dịch",
    "51": "Tài khoản không đủ số dư",
    "65": "Tài khoản đã vượt quá hạn mức giao dịch trong ngày",
    "75": "Ngân hàng thanh toán đang bảo trì",
    "79": "Nhập sai mật khẩu thanh toán quá số lần quy định",
    "99": "Lỗi khác",
}


def _get_required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is not set")
    return value


def _to_vnp_amount(amount):
    decimal_amount = Decimal(str(amount))
    return str(int(decimal_amount * 100))


def _normalize_order_info(order_info):
    value = str(order_info or "")
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9 .:_#-]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:255] or "Thanh toan don hang"


def _build_hash_data(params):
    sorted_params = sorted(params.items())
    return urlencode(sorted_params)


def _hmac_sha512(data, secret):
    return hmac.new(
        secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()


def build_payment_url(txn_ref, amount, order_info, ip_addr, bank_code=None):
    vnp_tmn_code = _get_required_env("VNP_TMN_CODE")
    vnp_hash_secret = _get_required_env("VNP_HASH_SECRET")
    vnp_payment_url = os.getenv(
        "VNP_PAYMENT_URL",
        "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    )
    vnp_return_url = _get_required_env("VNP_RETURN_URL")

    now = datetime.now(VN_TZ)

    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": vnp_tmn_code,
        "vnp_Amount": _to_vnp_amount(amount),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": str(txn_ref),
        "vnp_OrderInfo": _normalize_order_info(order_info),
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": vnp_return_url,
        "vnp_IpAddr": ip_addr,
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": (now + timedelta(minutes=15)).strftime("%Y%m%d%H%M%S"),
    }

    if bank_code:
        params["vnp_BankCode"] = bank_code

    hash_data = _build_hash_data(params)
    secure_hash = _hmac_sha512(hash_data, vnp_hash_secret)

    query_string = urlencode(sorted(params.items()))
    return f"{vnp_payment_url}?{query_string}&vnp_SecureHash={secure_hash}"


def verify_signature(params: dict) -> bool:
    vnp_hash_secret = _get_required_env("VNP_HASH_SECRET")

    secure_hash = params.get("vnp_SecureHash")
    if not secure_hash:
        return False

    clean_params = {}

    for key, value in params.items():
        if key in ["vnp_SecureHash", "vnp_SecureHashType"]:
            continue

        if not key.startswith("vnp_"):
            continue

        if value is None or value == "":
            continue

        clean_params[key] = str(value)

    hash_data = _build_hash_data(clean_params)
    expected_hash = _hmac_sha512(hash_data, vnp_hash_secret)

    return hmac.compare_digest(expected_hash, secure_hash)