// Restaurant: xem danh sách đơn hàng kanban
(function () {
    const API_BOARD = "/api/orders/board";
    const API_ORDER = (id) => `/api/orders/${id}`;
    const API_APPROVE = (id) => `/api/orders/${id}/approve`;
    const API_REJECT = (id) => `/api/orders/${id}/reject`;

    const detailModal = document.getElementById("order-detail-modal");
    const detailTitle = document.getElementById("order-detail-title");
    const detailStatus = document.getElementById("order-detail-status");
    const detailBody = document.getElementById("order-detail-body");

    const rejectModal = document.getElementById("reject-modal");
    const rejectOrderId = document.getElementById("reject-order-id");
    const rejectReason = document.getElementById("reject-reason");
    const rejectError = document.getElementById("reject-error");

    const searchInput = document.querySelector('input[name="keyword"]');
    const startInput = document.querySelector('input[name="start_date"]');
    const endInput = document.querySelector('input[name="end_date"]');

    const STATUS_LABELS = {
        PAID: "Mới",
        CONFIRMED: "Đã xác nhận",
        PREPARING: "Đang chế biến",
        DELIVERING: "Đang giao",
        COMPLETED: "Đã hoàn tất",
        CANCELLED: "Từ chối",
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
        return `${pad(date.getHours())}:${pad(date.getMinutes())} - ${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()}`;
    }

    function buildCard(o) {
        const items = (o.items || [])
            .slice(0, 3)
            .map((it) => `<li>${escapeHtml(it.quantity)}x ${escapeHtml(it.name)}</li>`)
            .join("");
        const more = (o.items_count || 0) > 3
            ? `<p class="text-xs text-secondary mt-1">${escapeHtml(o.items_count)} món / ${formatCurrency(o.subtotal)}</p>`
            : "";
        const actions = o.status !== "COMPLETED"
            ? `<div class="flex gap-2">
                    <button class="reject-order-btn p-2 text-error rounded-lg transition-all" data-order-id="${escapeHtml(o.id)}" type="button"><span class="material-symbols-outlined text-sm">close</span></button>
                    <button class="approve-order-btn px-4 py-2 bg-primary text-white rounded-lg font-label-md hover:scale-95 transition-all" data-order-id="${escapeHtml(o.id)}" type="button">Xác nhận</button>
               </div>`
            : "";
        const borderColor = o.status === "PAID" ? "primary"
            : o.status === "PREPARING" ? "tertiary"
            : "emerald-500";
        return `<div class="bg-surface-container-lowest rounded-xl p-5 shadow-[0px_4px_20px_rgba(0,0,0,0.05)] space-y-4 border-l-4 border-${borderColor} cursor-pointer hover:shadow-[0px_8px_30px_rgba(0,0,0,0.1)] transition-all" data-order-id="${escapeHtml(o.id)}" data-order-card>
            <div class="flex justify-between items-start">
                <div>
                    <p class="font-bold text-lg">${escapeHtml(o.code)}</p>
                    <p class="text-caption text-secondary">Khách: ${escapeHtml(o.customer_name)}</p>
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
                ${actions}
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
                    <p class="text-caption text-secondary uppercase tracking-wider font-bold">Khách hàng</p>
                    <p class="font-bold">${escapeHtml(order.customer_name)}</p>
                    <p>${escapeHtml(order.customer_phone || "")}</p>
                    <p>${escapeHtml(order.customer_email || "")}</p>
                </div>
                <div class="bg-surface-bright rounded-xl p-4 space-y-1">
                    <p class="text-caption text-secondary uppercase tracking-wider font-bold">Địa chỉ giao</p>
                    <p>${escapeHtml(order.delivery_address || "")}</p>
                    ${order.note ? `<p class="text-secondary">Ghi chú: ${escapeHtml(order.note)}</p>` : ""}
                </div>
            </div>
            <div class="bg-surface-bright rounded-xl p-4">
                <p class="text-caption text-secondary uppercase tracking-wider font-bold mb-2">Món ăn</p>
                <ul class="text-sm">${items || '<li class="text-secondary">Không có món</li>'}</ul>
            </div>
            <div class="bg-surface-bright rounded-xl p-4 space-y-1.5 text-sm">
                ${order.voucher ? `<p class="flex justify-between"><span>Voucher: ${escapeHtml(order.voucher.code)}</span><span class="font-semibold">${escapeHtml(order.voucher.name)}</span></p>` : ""}
                <p class="flex justify-between"><span>Tạm tính</span><span>${formatCurrency(order.subtotal)}</span></p>
                <p class="flex justify-between"><span>Phí ship</span><span>${formatCurrency(order.shipping_fee)}</span></p>
                <p class="flex justify-between font-bold text-primary text-base"><span>Tổng</span><span>${formatCurrency(order.total_amount)}</span></p>
                ${order.rejection_reason ? `<p class="mt-2 text-error">Lý do từ chối: ${escapeHtml(order.rejection_reason)}</p>` : ""}
            </div>
        `;
        detailModal.classList.remove("hidden");
    }

    function openRejectModal(orderId) {
        rejectOrderId.value = orderId;
        rejectReason.value = "";
        rejectError.classList.add("hidden");
        rejectModal.classList.remove("hidden");
    }

    function closeRejectModal() {
        rejectModal.classList.add("hidden");
    }

    function closeDetailModal() {
        detailModal.classList.add("hidden");
    }

    function setLoading(btn, loading) {
        btn.disabled = loading;
        if (loading) {
            btn.dataset.original = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-dot"></span>';
        } else {
            btn.innerHTML = btn.dataset.original || btn.innerHTML;
        }
    }

    function confetti(x, y) {
        const colors = ["#1f6b4e", "#ffd166", "#b3261e", "#4ade80", "#60a5fa"];
        for (let i = 0; i < 14; i++) {
            const p = document.createElement("span");
            p.className = "confetti";
            p.style.background = colors[i % colors.length];
            p.style.left = x + "px";
            p.style.top = y + "px";
            p.style.transform = `rotate(${Math.random() * 360}deg)`;
            document.body.appendChild(p);
            const dx = (Math.random() - .5) * 160;
            const dy = -40 - Math.random() * 120;
            p.animate(
                [{ transform: "rotate(0)", opacity: 1 }, { transform: `translate(${dx}px, ${dy}px) rotate(${360 + Math.random() * 180}deg)`, opacity: 0 }],
                { duration: 700 + Math.random() * 400, easing: "cubic-bezier(.2,.8,.4,1)" }
            ).onfinish = () => p.remove();
        }
    }

    function bumpCount(status, delta) {
        const col = document.querySelector(`[data-status="${status}"]`);
        if (!col) return;
        const badge = col.querySelector("[data-total]");
        if (!badge) return;
        const n = (parseInt(badge.dataset.total, 10) || 0) + delta;
        badge.dataset.total = n;
        badge.textContent = `${n} ĐƠN`;
    }

    function popCard(card, toStatus) {
        const rect = card.getBoundingClientRect();
        confetti(rect.left + rect.width / 2, rect.top + rect.height / 2);
        const fromStatus = card.closest("[data-status]").dataset.status;
        bumpCount(fromStatus, -1);
        card.classList.add("card-out");
        setTimeout(() => {
            card.remove();
            if (!toStatus) return;
            const toCol = document.querySelector(`[data-status="${toStatus}"]`);
            if (!toCol) return;
            const el = card.cloneNode(true);
            el.classList.remove("card-out");
            el.classList.add("card-pop");
            if (toStatus === "COMPLETED") {
                const actions = el.querySelector(".flex.gap-2");
                if (actions) actions.remove();
                el.classList.remove("border-primary", "border-tertiary");
                el.classList.add("border-emerald-500");
            }
            toCol.querySelector(".space-y-4").appendChild(el);
            bumpCount(toStatus, 1);
            el.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }, 500);
    }

    function renderColumn(status, data) {
        const col = document.querySelector(`[data-status="${status}"]`);
        if (!col) return;
        const badge = col.querySelector("[data-total]");
        if (badge) {
            badge.dataset.total = data.total;
            badge.textContent = `${data.total} ĐƠN`;
        }
        const container = col.querySelector(".space-y-4");
        container.innerHTML = data.items.map(buildCard).join("");
        const oldMore = col.querySelector(".load-more-btn");
        if (oldMore) oldMore.remove();
        if (data.has_more) {
            const btn = document.createElement("button");
            btn.className = "load-more-btn w-full py-2 bg-surface-container-high text-secondary rounded-lg font-label-md hover:bg-surface-container transition-colors";
            btn.dataset.status = status;
            btn.dataset.page = "2";
            const pageSize = Number(document.querySelector("[data-board]")?.dataset.pageSize || 4);
            btn.textContent = `Xem thêm (${data.total - pageSize} đơn còn lại)`;
            col.appendChild(btn);
        }
    }

    let filterSeq = 0;
    function applyFilter() {
        const seq = ++filterSeq;
        const keyword = searchInput.value.trim();
        const startDate = startInput.value;
        const endDate = endInput.value;
        const url = new URL(window.location.href);
        url.searchParams.set("keyword", keyword);
        url.searchParams.set("start_date", startDate);
        url.searchParams.set("end_date", endDate);
        history.replaceState(null, "", url);
        const pageSize = document.querySelector("[data-board]")?.dataset.pageSize || "4";
        ["PAID", "PREPARING", "COMPLETED"].forEach(async (status) => {
            const params = new URLSearchParams({
                status, page: "1", per_page: pageSize,
                keyword, start_date: startDate, end_date: endDate,
            });
            const resp = await fetch(`${API_BOARD}?${params.toString()}`);
            const data = await resp.json();
            if (seq !== filterSeq || !data.success) return;
            renderColumn(status, data);
        });
    }

    let debounceTimer;
    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(applyFilter, 350);
    });
    startInput.addEventListener("change", applyFilter);
    endInput.addEventListener("change", applyFilter);

    document.addEventListener("click", function (e) {
        const approveBtn = e.target.closest(".approve-order-btn");
        if (approveBtn) {
            const orderId = approveBtn.dataset.orderId;
            const card = approveBtn.closest("[data-order-card]");
            setLoading(approveBtn, true);
            fetch(API_APPROVE(orderId), { method: "PATCH" })
                .then((r) => r.json().then((data) => ({ ok: r.ok, data })))
                .then(({ ok, data }) => {
                    setLoading(approveBtn, false);
                    if (!ok) {
                        window.showToast(data.message || "Lỗi", "error");
                        return;
                    }
                    popCard(card, data.order && data.order.status);
                    window.showToast(data.message || "Đã xử lý", "success");
                })
                .catch(() => {
                    setLoading(approveBtn, false);
                    window.showToast("Lỗi kết nối", "error");
                });
            return;
        }

        const rejectBtn = e.target.closest(".reject-order-btn");
        if (rejectBtn) {
            openRejectModal(rejectBtn.dataset.orderId);
            return;
        }

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
                    window.showToast(data.message || "Lỗi", "error");
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
            .catch(() => window.showToast("Lỗi kết nối", "error"));
    });

    document.getElementById("close-order-detail-btn").addEventListener("click", closeDetailModal);
    document.getElementById("order-detail-backdrop").addEventListener("click", closeDetailModal);

    document.getElementById("confirm-reject-btn").addEventListener("click", function () {
        const orderId = rejectOrderId.value;
        const reason = rejectReason.value.trim();
        if (!reason) {
            rejectError.textContent = "Vui lòng nhập lý do từ chối";
            rejectError.classList.remove("hidden");
            return;
        }
        const btn = document.getElementById("confirm-reject-btn");
        setLoading(btn, true);
        fetch(API_REJECT(orderId), {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reason }),
        })
            .then((r) => r.json().then((data) => ({ ok: r.ok, data })))
            .then(({ ok, data }) => {
                setLoading(btn, false);
                if (!ok) {
                    window.showToast(data.message || "Lỗi", "error");
                    return;
                }
                closeRejectModal();
                const card = document.querySelector(`[data-order-card][data-order-id="${orderId}"]`);
                if (card) popCard(card, null);
                window.showToast(data.message, "success");
            })
            .catch(() => {
                setLoading(btn, false);
                rejectError.textContent = "Lỗi kết nối";
                rejectError.classList.remove("hidden");
            });
    });

    document.getElementById("close-reject-modal-btn").addEventListener("click", closeRejectModal);
    document.getElementById("cancel-reject-btn").addEventListener("click", closeRejectModal);
    document.getElementById("reject-modal-backdrop").addEventListener("click", closeRejectModal);
})();
