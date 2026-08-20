// Restaurant: xem danh sách đơn hàng kanban
(function () {
    const API_BOARD = "/api/orders/board";
    const API_ORDER = (id) => `/api/orders/${id}`;

    const detailModal = document.getElementById("order-detail-modal");
    const detailTitle = document.getElementById("order-detail-title");
    const detailStatus = document.getElementById("order-detail-status");
    const detailBody = document.getElementById("order-detail-body");

    const STATUS_LABELS = {
        PAID: "Moi",
        CONFIRMED: "Da xac nhan",
        PREPARING: "Dang che bien",
        DELIVERING: "Dang giao",
        COMPLETED: "Da hoan tat",
        CANCELLED: "Tu choi",
    };

    function escapeHtml(value) {
        if (value === null || value === undefined) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function formatCurrency(value) {
        if (value === null || value === undefined || value === "") return "-";
        return new Intl.NumberFormat("vi-VN").format(Number(value)) + " đ";
    }

    function formatDateTime(value) {
        if (!value) return "-";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "-";
        const pad = (number) => String(number).padStart(2, "0");
        return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
    }

    function buildCard(o) {
        const items = (o.items || [])
            .slice(0, 3)
            .map((it) => `<li>${escapeHtml(it.quantity)}x ${escapeHtml(it.name)}</li>`)
            .join("");
        const more = (o.items_count || 0) > 3
            ? `<p class="text-xs text-secondary mt-1">${escapeHtml(o.items_count)} mon / ${formatCurrency(o.subtotal)}</p>`
            : "";
        const borderColor = o.status === "PAID" ? "primary"
            : o.status === "PREPARING" ? "tertiary"
            : "secondary";
        return `<div class="bg-surface-container-lowest rounded-xl p-5 shadow-[0px_4px_20px_rgba(0,0,0,0.05)] space-y-4 border-l-4 border-${borderColor}" data-order-id="${escapeHtml(o.id)}">
            <div class="flex justify-between items-start">
                <div>
                    <p class="font-bold text-lg">${escapeHtml(o.code)}</p>
                    <p class="text-caption text-secondary">Khach: ${escapeHtml(o.customer_name)}</p>
                    <p class="text-caption text-secondary">${escapeHtml(o.customer_phone || "")}</p>
                </div>
                <span class="text-caption bg-surface-container-highest px-2 py-1 rounded">${formatDateTime(o.created_at)}</span>
            </div>
            <div class="py-3 border-y border-outline-variant/30">
                <ul class="text-sm space-y-1 text-secondary">${items}</ul>
                ${more}
            </div>
            <div class="flex justify-between items-center">
                <span class="font-bold text-primary">${formatCurrency(o.total_amount)}</span>
            </div>
        </div>`;
    }

    function openDetailModal(order) {
        detailTitle.textContent = order.code || "";
        detailStatus.textContent = STATUS_LABELS[order.status] || order.status || "";

        const items = (order.items || [])
            .map((it) => `<li class="flex justify-between gap-4 py-1.5 border-b border-outline-variant/30 last:border-0">
                <span>${escapeHtml(it.quantity)}x ${escapeHtml(it.name)}</span>
                <span class="font-semibold">${formatCurrency(it.unit_price * it.quantity)}</span>
            </li>`)
            .join("");

        detailBody.innerHTML = `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-surface-bright rounded-xl p-4 space-y-1">
                    <p class="text-caption text-secondary uppercase tracking-wider font-bold">Khach hang</p>
                    <p class="font-bold">${escapeHtml(order.customer_name)}</p>
                    <p>${escapeHtml(order.customer_phone || "")}</p>
                    <p>${escapeHtml(order.customer_email || "")}</p>
                </div>
                <div class="bg-surface-bright rounded-xl p-4 space-y-1">
                    <p class="text-caption text-secondary uppercase tracking-wider font-bold">Dia chi giao</p>
                    <p>${escapeHtml(order.delivery_address || "")}</p>
                    ${order.note ? `<p class="text-secondary">Ghi chu: ${escapeHtml(order.note)}</p>` : ""}
                </div>
            </div>
            <div class="bg-surface-bright rounded-xl p-4">
                <p class="text-caption text-secondary uppercase tracking-wider font-bold mb-2">Mon an</p>
                <ul class="text-sm">${items || '<li class="text-secondary">Khong co mon</li>'}</ul>
            </div>
            <div class="bg-surface-bright rounded-xl p-4 space-y-1.5 text-sm">
                ${order.voucher ? `<p class="flex justify-between"><span>Voucher: ${escapeHtml(order.voucher.code)}</span><span class="font-semibold">${escapeHtml(order.voucher.name)}</span></p>` : ""}
                <p class="flex justify-between"><span>Tam tinh</span><span>${formatCurrency(order.subtotal)}</span></p>
                <p class="flex justify-between"><span>Phi ship</span><span>${formatCurrency(order.shipping_fee)}</span></p>
                <p class="flex justify-between font-bold text-primary text-base"><span>Tong</span><span>${formatCurrency(order.total_amount)}</span></p>
                ${order.rejection_reason ? `<p class="mt-2 text-error">Ly do tu choi: ${escapeHtml(order.rejection_reason)}</p>` : ""}
            </div>
        `;
        detailModal.classList.remove("hidden");
    }

    function closeDetailModal() {
        detailModal.classList.add("hidden");
    }

    document.addEventListener("click", function (e) {
        const card = e.target.closest("[data-order-card]");
        if (card) {
            const orderId = card.dataset.orderId;
            fetch(API_ORDER(orderId))
                .then((r) => r.json())
                .then((data) => {
                    if (data.success) openDetailModal(data.order);
                })
                .catch(() => {});
            return;
        }

        const loadMoreBtn = e.target.closest(".load-more-btn");
        if (!loadMoreBtn) return;

        const status = loadMoreBtn.dataset.status;
        const nextPage = Number(loadMoreBtn.dataset.page);
        const container = loadMoreBtn.closest(".space-y-4").querySelector(".space-y-4");
        const board = document.querySelector("[data-board]");
        const params = new URLSearchParams(window.location.search);
        params.set("status", status);
        params.set("page", nextPage);
        params.set("per_page", (board && board.dataset.pageSize) || "4");

        fetch(`${API_BOARD}?${params.toString()}`)
            .then((r) => r.json())
            .then((data) => {
                if (!data.success) {
                    window.showToast(data.message || "Loi", "error");
                    return;
                }
                data.items.forEach((o) => {
                    container.insertAdjacentHTML("beforeend", buildCard(o));
                });
                if (data.has_more) {
                    loadMoreBtn.dataset.page = nextPage + 1;
                } else {
                    loadMoreBtn.remove();
                }
            })
            .catch(() => window.showToast("Loi ket noi", "error"));
    });

    document.getElementById("close-order-detail-btn").addEventListener("click", closeDetailModal);
    document.getElementById("order-detail-backdrop").addEventListener("click", closeDetailModal);
})();
