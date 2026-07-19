from flask import redirect, url_for
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.models.model import UserRole


def _is_admin():
    return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class AdminSecureView(ModelView):
    def is_accessible(self):
        return _is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_bp.login_page'))


class AdminSecureIndexView(AdminIndexView):
    def is_accessible(self):
        return _is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_bp.login_page'))


class UserAdmin(AdminSecureView):
    column_exclude_list = ['password']
    form_excluded_columns = ['password']
    column_searchable_list = ['name', 'username', 'email']
    column_filters = ['role', 'active', 'auth_provider']
    column_labels = {
        'name': 'Tên',
        'username': 'Tên đăng nhập',
        'email': 'Email',
        'phonenumber': 'Số điện thoại',
        'role': 'Vai trò',
        'active': 'Kích hoạt',
        'created_at': 'Ngày tạo',
    }


class RestaurantAdmin(AdminSecureView):
    column_searchable_list = ['name']
    column_filters = ['cuisine_type', 'status', 'active']
    column_sortable_list = ['name', 'cuisine_type', 'active', 'created_at']
    column_default_sort = ('active', False)

    column_labels = {
        'name': 'Tên nhà hàng',
        'description': 'Mô tả',
        'cuisine_type': 'Loại ẩm thực',
        'status': 'Đang mở',
        'active': 'Duyệt',
        'opening_time': 'Giờ mở cửa',
        'closing_time': 'Giờ đóng cửa',
        'tax_code': 'Mã số thuế',
    }

    column_list = ['name', 'cuisine_type', 'active']


class DishAdmin(AdminSecureView):
    column_searchable_list = ['name']
    column_filters = ['category', 'active']
    column_labels = {
        'name': 'Tên món',
        'description': 'Mô tả',
        'price': 'Giá',
        'category': 'Danh mục',
        'restaurant': 'Nhà hàng',
    }
