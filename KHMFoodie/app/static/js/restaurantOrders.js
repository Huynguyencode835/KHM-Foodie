// Restaurant: xem danh sách đơn hàng kanban
(function () {
    const API_BOARD = "/api/orders/board";

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

    document.addEventListener("click", function (e) {
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
})();
