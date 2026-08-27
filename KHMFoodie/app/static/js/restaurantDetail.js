const pathParts = window.location.pathname.split('/');
const restaurantId = window.RESTAURANT_ID || pathParts[pathParts.length - 1];
const isRestaurantMenuPage = Boolean(window.RESTAURANT_ID);

function formatPrice(value) {
    return `${(value || 0).toLocaleString('vi-VN')}đ`;
}

async function fetchCart() {
    const res = await fetch(`/api/cart/${restaurantId}`);
    if (!res.ok) return null;
    return res.json();
}

function renderCart(cart) {
    const container = document.getElementById('cart-items');
    const items = (cart && cart.items) || [];

    container.innerHTML = '';
    items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'flex justify-between items-center py-xs border-b border-outline-variant/10';
        row.innerHTML = `
            <div>
                <p class="font-label-md">${item.dish_name}</p>
                <p class="text-caption text-secondary">${formatPrice(item.price)}</p>
            </div>
            <div class="flex items-center gap-xs">
                <button class="w-6 h-6 rounded-full border border-outline-variant flex items-center justify-center text-secondary hover:bg-primary hover:text-white hover:border-primary active:scale-90 transition-all"
                    onclick="changeCartItemQuantity(${item.id}, ${item.quantity - 1})">
                    <span class="material-symbols-outlined text-sm">remove</span>
                </button>
                <span class="font-label-md w-4 text-center">${item.quantity}</span>
                <button class="w-6 h-6 rounded-full border border-outline-variant flex items-center justify-center text-secondary hover:bg-primary hover:text-white hover:border-primary active:scale-90 transition-all"
                    onclick="changeCartItemQuantity(${item.id}, ${item.quantity + 1})">
                    <span class="material-symbols-outlined text-sm">add</span>
                </button>
            </div>
        `;
        container.appendChild(row);
    });

    const total = cart ? cart.total : 0;
    document.getElementById('cart-subtotal').textContent = formatPrice(total);
    document.getElementById('cart-total').textContent = formatPrice(total);
    document.getElementById('checkout-btn').disabled = items.length === 0;
    document.getElementById('mobile-cart-count').textContent = items.reduce((sum, i) => sum + i.quantity, 0);
    document.getElementById('mobile-cart-total').textContent = formatPrice(total);
}

async function refreshCart() {
    const cart = await fetchCart();
    renderCart(cart);
}

async function addToCart(dishId) {
    const res = await fetch(`/api/cart/${restaurantId}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dish_id: dishId, quantity: 1 })
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        window.showToast(err.message || 'Không thể thêm món vào giỏ hàng', 'error');
        return;
    }
    await refreshCart();
}

async function changeCartItemQuantity(cartItemId, newQuantity) {
    const res = newQuantity <= 0
        ? await fetch(`/api/cart/${restaurantId}/items/${cartItemId}`, { method: 'DELETE' })
        : await fetch(`/api/cart/${restaurantId}/items/${cartItemId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: newQuantity })
        });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        window.showToast(err.message || 'Không thể cập nhật giỏ hàng', 'error');
        return;
    }
    await refreshCart();
}

// load data restaurent detail and list dishes

async function fetchRestaurantData(id) {
    const res = await fetch(`/api/restaurants/${id}`);
    if (!res.ok) return null;
    return res.json();
}

async function fetchDishesData(id, page, category, keyword) {
    const params = new URLSearchParams({ page, per_page: 12 });
    if (category && category !== 'all') params.append('category', category);
    if (keyword) params.append('q', keyword);
    const res = await fetch(`/api/restaurants/${id}/dishes?${params}`);
    if (!res.ok) return { data: [], pages: 1 };
    const json = await res.json();
    return { data: json.data || [], pages: json.pages || 1 };
}

function renderRestaurantDetail(data) {
    if (!data) return;

    let el;

    el = document.querySelector('[data-restaurant-name]');
    if (el) el.textContent = data.name;
    el = document.querySelector('[data-restaurant-hero]');
    if (el) el.style.backgroundImage = `url('${data.cover_image || data.avatar}')`;
    el = document.querySelector('[data-restaurant-address]');
    if (el) el.textContent = data.address;
    el = document.querySelector('[data-restaurant-cuisine]');
    if (el) el.textContent = data.cuisine_type;
    el = document.querySelector('[data-restaurant-hours]');
    if (el && data.opening_time) el.textContent = `${data.opening_time} - ${data.closing_time}`;

    el = document.querySelector('[data-restaurant-name-sidebar]');
    if (el) el.textContent = data.name;

    el = document.querySelector('[data-restaurant-info-description]');
    if (el) el.textContent = data.description;
    el = document.querySelector('[data-restaurant-info-address]');
    if (el) el.textContent = data.address;
    el = document.querySelector('[data-restaurant-info-hours]');
    if (el && data.opening_time) el.textContent = `${data.opening_time} - ${data.closing_time}`;
    el = document.querySelector('[data-restaurant-info-phone]');
    if (el) el.textContent = data.phonenumber;
    el = document.querySelector('[data-restaurant-info-email]');
    if (el) el.textContent = data.email;

    el = document.querySelector('[data-restaurant-status]');
    if (el && data.opening_time) {
        const now = new Date();
        const [openH, openM] = data.opening_time.split(':').map(Number);
        const [closeH, closeM] = data.closing_time.split(':').map(Number);
        const open = openH * 60 + openM;
        const close = closeH * 60 + closeM;
        const current = now.getHours() * 60 + now.getMinutes();
        const isOpen = current >= open && current < close;
        el.textContent = isOpen ? 'Đang mở' : 'Đã đóng';
        el.className = `px-sm py-base rounded-full font-label-md text-label-md ${isOpen ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`;
    }

    if (data.distance_km) {
        el = document.querySelector('[data-restaurant-distance]');
        if (el) el.textContent = data.distance_km;
    }
    if (data.delivery_fee) {
        el = document.querySelector('[data-restaurant-fee]');
        if (el) el.textContent = data.delivery_fee;
    }

    document.title = `${data.name} - CraveConnect`;

}

function renderDishes(dishes, emptyMessage = 'Chưa có món ăn nào', showAction = !isRestaurantMenuPage) {
    console.log(dishes)
    const container = document.getElementById('dish-grid');
    if (!container) return;

    if (!dishes || dishes.length === 0) {
        container.innerHTML = `
            <div class="col-span-full text-center py-xl text-on-surface-variant">
                <span class="material-symbols-outlined text-5xl mb-sm">restaurant_menu</span>
                <p class="text-body-md">${emptyMessage}</p>
            </div>`;
        return;
    }

    container.innerHTML = dishes.map(d => `
        <div class="bg-surface-container-lowest rounded-xl shadow-lg border border-transparent hover:border-primary-fixed hover:shadow-lg hover:-translate-y-1 transition-all duration-300 overflow-hidden group flex flex-col ${d.active ? '' : 'dish-disabled'}">
            <div class="h-40 bg-cover rounded-xl bg-center relative" style="background-image: url('${d.image || ''}')">
                <img src="${d.image || ''}" onerror="this.parentElement.style.backgroundImage='url(https://png.pngtree.com/png-vector/20210623/ourmid/pngtree-pho-noodle-vietnamese-food-png-png-image_3508276.jpg)'" class="hidden">
                ${showAction ? '' : `
                <label class="dish-select-label absolute top-2 left-2 w-6 h-6 rounded-full bg-white shadow cursor-pointer z-10" title="Chọn để xóa">
                    <input type="checkbox" class="dish-select-input sr-only">
                    <span class="dish-select-check material-symbols-outlined text-sm text-transparent">check</span>
                </label>
                `}
            </div>
            <div class="p-sm flex flex-col flex-1">
                <h3 class="font-headline-lg font-bold line-clamp-1">${d.name}</h3>
                <span class="text-caption text-secondary mb-xs">${d.category || ''}</span>
                <p class="text-sm text-gray-500 italic line-clamp-2 mb-sm flex-1">${d.description || ''}</p>
                ${showAction ? `
                <div class="flex items-center justify-between gap-sm pt-xs border-t border-outline-variant/10">
                    <span class="font-headline-md text-primary whitespace-nowrap">${(d.price || 0).toLocaleString('vi-VN')}đ</span>
                    <button class="shrink-0 py-xs px-md bg-surface-container-highest text-primary rounded-lg font-label-md hover:bg-primary hover:text-white transition-all flex items-center gap-xs"
                        onclick="addToCart(${d.id})">
                        <span class="material-symbols-outlined text-sm">add</span> Thêm
                    </button>
                </div>
                ` : `
                <div class="flex items-center justify-between gap-sm pt-xs border-t border-outline-variant/10">
                    <span class="font-headline-md text-primary whitespace-nowrap">${(d.price || 0).toLocaleString('vi-VN')}đ</span>
                    <div class="flex items-center gap-sm shrink-0">
                        <label class="dish-toggle relative inline-flex items-center cursor-pointer" title="Bật / tắt món ăn">
                            <input type="checkbox" class="dish-toggle-input sr-only" ${d.active ? 'checked' : ''}>
                            <span class="dish-toggle-track w-10 h-5 bg-secondary-fixed rounded-full relative transition-colors">
                                <span class="dish-toggle-dot absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"></span>
                            </span>
                        </label>
                        <button class="dish-delete-btn w-7 h-7 rounded-lg border border-outline-variant flex items-center justify-center text-secondary hover:bg-error-container hover:text-error transition-all" data-dish-id="${d.id}" title="Xóa món ăn">
                            <span class="material-symbols-outlined text-sm">delete</span>
                        </button>
                    </div>
                </div>
                `}
            </div>
        </div>
    `).join('');
}

let currentCategory = 'all';

async function applyDishFilters() {
    currentPage = 1;
    const dishSearchInput = document.getElementById('dish-search-input');
    const keyword = dishSearchInput ? dishSearchInput.value.trim().toLowerCase() : '';

    const result = await fetchDishesData(restaurantId, 1, currentCategory, keyword);
    renderDishes(result.data, 'Không tìm thấy món ăn phù hợp');
    totalPages = result.pages;
    renderPagination();
}


document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const tab = this.dataset.tab;

        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.remove('border-primary', 'text-primary');
            b.classList.add('border-transparent', 'text-secondary');
        });
        this.classList.remove('border-transparent', 'text-secondary');
        this.classList.add('border-primary', 'text-primary');

        document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
        document.getElementById('tab-' + tab).classList.remove('hidden');
    });
});

async function goToPage(page) {
    if (page < 1 || page > totalPages || page === currentPage) return;
    currentPage = page;
    const dishSearchInput = document.getElementById('dish-search-input');
    const keyword = dishSearchInput ? dishSearchInput.value.trim().toLowerCase() : '';
    const result = await fetchDishesData(restaurantId, currentPage, currentCategory, keyword);
    renderDishes(result.data);
    renderPagination();
}

document.addEventListener('DOMContentLoaded', async function () {
    if (!restaurantId) return;

    const checkoutButton = document.getElementById('checkout-btn');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', () => {
            if (!checkoutButton.disabled) {
                window.location.href = `/payment/${restaurantId}`;
            }
        });
    }

    const [data] = await Promise.all([
        document.querySelector('[data-restaurant-name]') ? fetchRestaurantData(restaurantId) : Promise.resolve(null),
        document.getElementById('cart-items') ? refreshCart() : Promise.resolve()
    ]);

    renderRestaurantDetail(data);

    currentPage = 1;
    await applyDishFilters();
    bindPaginationButtons();

    let searchTimeout;
    const dishSearchInput = document.getElementById('dish-search-input');
    if (dishSearchInput) {
        dishSearchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyDishFilters, 300);
        });
    }

    document.querySelectorAll('.dish-category-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            currentCategory = this.dataset.category;

            document.querySelectorAll('.dish-category-btn').forEach(b => {
                b.classList.remove('bg-primary', 'text-white');
                b.classList.add('bg-transparent', 'text-secondary');
            });

            this.classList.remove('bg-transparent', 'text-secondary');
            this.classList.add('bg-primary', 'text-white');

            applyDishFilters();
        });
    });

});
