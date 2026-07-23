const pathParts = window.location.pathname.split('/');
const restaurantId = pathParts[pathParts.length - 1];

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
        alert('Không thể thêm món vào giỏ hàng');
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
        alert('Không thể cập nhật giỏ hàng');
        return;
    }
    await refreshCart();
}

document.addEventListener('DOMContentLoaded', refreshCart);
