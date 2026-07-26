(function () {
    const API_URL = "/api/promotions";

    const state = {
        vouchers: [],
        filtered: [],
    };

    const els = {
        loading: document.getElementById("voucher-loading"),
        error: document.getElementById("voucher-error"),
        empty: document.getElementById("voucher-empty"),
        list: document.getElementById("voucher-list"),
        search: document.getElementById("voucher-search-input"),
        total: document.getElementById("voucher-stat-total"),
        active: document.getElementById("voucher-stat-active"),
        expiring: document.getElementById("voucher-stat-expiring"),
        refreshBtn: document.getElementById("refresh-vouchers-btn"),
        openCreateBtn: document.getElementById("open-create-modal-btn"),
        modal: document.getElementById("voucher-modal"),
        backdrop: document.getElementById("voucher-modal-backdrop"),
        closeModalBtn: document.getElementById("close-voucher-modal-btn"),
        cancelBtn: document.getElementById("cancel-voucher-btn"),
        modalTitle: document.getElementById("voucher-modal-title"),
        form: document.getElementById("voucher-form"),
        submitBtn: document.getElementById("voucher-submit-btn"),
        formError: document.getElementById("voucher-form-error"),
        id: document.getElementById("voucher-id"),
        name: document.getElementById("voucher-name"),
        code: document.getElementById("voucher-code"),
        description: document.getElementById("voucher-description"),
        discountType: document.getElementById("voucher-discount-type"),
        discountValue: document.getElementById("voucher-discount-value"),
        minimumOrder: document.getElementById("voucher-minimum-order"),
        maxDiscount: document.getElementById("voucher-max-discount"),
        usageLimit: document.getElementById("voucher-usage-limit"),
        startDate: document.getElementById("voucher-start-date"),
        endDate: document.getElementById("voucher-end-date"),
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

    function toDatetimeLocalValue(value) {
        if (!value) return "";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "";
        const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
        return local.toISOString().slice(0, 16);
    }

    function showLoading(isLoading) {
        els.loading.classList.toggle("hidden", !isLoading);
    }

    function showError(message) {
        els.error.textContent = message || "";
        els.error.classList.toggle("hidden", !message);
    }

    function showEmpty(isEmpty) {
        els.empty.classList.toggle("hidden", !isEmpty);
    }

    function clearFormErrors() {
        els.formError.textContent = "";
        els.formError.classList.add("hidden");

        document.querySelectorAll("[data-error-for]").forEach((node) => {
            node.textContent = "";
            node.classList.add("hidden");
        });
    }

    function setFormError(message) {
        els.formError.textContent = message;
        els.formError.classList.remove("hidden");
    }

    function setFieldError(fieldId, message) {
        const node = document.querySelector(`[data-error-for="${fieldId}"]`);
        if (!node) return;
        node.textContent = message;
        node.classList.remove("hidden");
    }

    function getVoucherStatus(voucher) {
        const now = new Date();
        const start = voucher.start_date ? new Date(voucher.start_date) : null;
        const end = voucher.end_date ? new Date(voucher.end_date) : null;

        if (start && now < start) return "Sắp áp dụng";
        if (end && now > end) return "Hết hạn";
        if (end) {
            const diffDays = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
            if (diffDays <= 3) return "Sắp hết hạn";
        }
        return "Đang hoạt động";
    }

    function getStatusBadgeClass(label) {
        if (label === "Đang hoạt động") return "bg-green-500/10 text-green-600";
        if (label === "Sắp hết hạn") return "bg-tertiary-fixed text-on-tertiary-fixed-variant";
        if (label === "Sắp áp dụng") return "bg-primary-fixed text-on-primary-fixed-variant";
        return "bg-secondary-container text-on-secondary-container";
    }

    function renderStats(allItems) {
        const now = new Date();
        const activeCount = allItems.filter((voucher) => {
            const start = voucher.start_date ? new Date(voucher.start_date) : null;
            const end = voucher.end_date ? new Date(voucher.end_date) : null;
            return (!start || now >= start) && (!end || now <= end);
        }).length;

        const expiringSoonCount = allItems.filter((voucher) => {
            if (!voucher.end_date) return false;
            const end = new Date(voucher.end_date);
            const diffDays = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
            return diffDays >= 0 && diffDays <= 3;
        }).length;

        els.total.textContent = allItems.length;
        els.active.textContent = activeCount;
        els.expiring.textContent = expiringSoonCount;
    }

    function renderRows(items) {
        renderStats(state.vouchers);

        if (!items.length) {
            els.list.innerHTML = "";
            showEmpty(true);
            return;
        }

        showEmpty(false);
        els.list.innerHTML = items.map((voucher) => {
            const statusLabel = getVoucherStatus(voucher);
            const discountLabel = voucher.discount_type === "PERCENTAGE"
                ? `${voucher.discount_value}%`
                : formatCurrency(voucher.discount_value);
            const conditionLabel = [
                `Đơn từ ${formatCurrency(voucher.minimum_order || 0)}`,
                voucher.max_discount ? `Tối đa ${formatCurrency(voucher.max_discount)}` : null,
            ].filter(Boolean).join(" • ");

            return `
                <article class="rounded-2xl border border-outline-variant bg-surface-bright p-5 shadow-sm">
                    <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                        <div class="space-y-3 flex-1">
                            <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                                <div>
                                    <div class="flex flex-wrap items-center gap-3">
                                        <h4 class="font-headline-md text-headline-md text-on-surface">${escapeHtml(voucher.name)}</h4>
                                        <span class="px-3 py-1 rounded-full text-caption font-bold ${getStatusBadgeClass(statusLabel)}">${escapeHtml(statusLabel)}</span>
                                    </div>
                                    <p class="text-label-md text-primary font-bold mt-1">${escapeHtml(voucher.code)}</p>
                                </div>
                                <div class="flex items-center gap-2">
                                    <button type="button" data-action="edit" data-id="${voucher.id}" class="px-3 py-2 rounded-lg bg-surface-container-low text-secondary hover:bg-surface-container transition-colors font-bold">Sửa</button>
                                    <button type="button" data-action="delete" data-id="${voucher.id}" class="px-3 py-2 rounded-lg bg-error-container text-error hover:bg-error hover:text-white transition-colors font-bold">Xóa</button>
                                </div>
                            </div>

                            <p class="text-body-md text-secondary">${escapeHtml(voucher.description || "Chưa có mô tả cho voucher này.")}</p>

                            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
                                <div class="rounded-xl bg-surface-container-lowest p-4">
                                    <p class="text-caption text-secondary uppercase tracking-wide">Loại giảm</p>
                                    <p class="text-body-md font-bold text-on-surface mt-2">${voucher.discount_type === "PERCENTAGE" ? "Phần trăm" : "Số tiền cố định"}</p>
                                </div>
                                <div class="rounded-xl bg-surface-container-lowest p-4">
                                    <p class="text-caption text-secondary uppercase tracking-wide">Giá trị</p>
                                    <p class="text-body-md font-bold text-on-surface mt-2">${escapeHtml(discountLabel)}</p>
                                </div>
                                <div class="rounded-xl bg-surface-container-lowest p-4">
                                    <p class="text-caption text-secondary uppercase tracking-wide">Điều kiện</p>
                                    <p class="text-body-md font-bold text-on-surface mt-2">${escapeHtml(conditionLabel)}</p>
                                </div>
                                <div class="rounded-xl bg-surface-container-lowest p-4">
                                    <p class="text-caption text-secondary uppercase tracking-wide">Lượt dùng</p>
                                    <p class="text-body-md font-bold text-on-surface mt-2">${voucher.used_count}/${voucher.usage_limit}</p>
                                </div>
                            </div>
                        </div>

                        <div class="xl:w-72 rounded-2xl bg-surface-container-lowest p-4">
                            <p class="text-caption text-secondary uppercase tracking-wide">Thời gian áp dụng</p>
                            <p class="text-body-md font-bold text-on-surface mt-2">${escapeHtml(formatDateTime(voucher.start_date))}</p>
                            <p class="text-body-md text-secondary mt-1">đến ${escapeHtml(formatDateTime(voucher.end_date))}</p>
                        </div>
                    </div>
                </article>
            `;
        }).join("");
    }

    function applyFilter() {
        const keyword = (els.search?.value || "").trim().toLowerCase();
        state.filtered = !keyword
            ? [...state.vouchers]
            : state.vouchers.filter((voucher) => {
                return [voucher.code, voucher.name, voucher.description]
                    .filter(Boolean)
                    .some((value) => String(value).toLowerCase().includes(keyword));
            });

        els.empty.textContent = keyword
            ? "Không tìm thấy voucher phù hợp."
            : "Chưa có voucher nào. Hãy tạo voucher đầu tiên.";
        renderRows(state.filtered);
    }

    async function loadVouchers() {
        showLoading(true);
        showError("");

        try {
            const res = await fetch(API_URL);
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.message || "Tải danh sách voucher thất bại");
            }

            state.vouchers = data.items || [];
            applyFilter();
        } catch (err) {
            state.vouchers = [];
            renderRows([]);
            showError(err.message || "Lỗi kết nối máy chủ");
        } finally {
            showLoading(false);
        }
    }

    function openModal() {
        els.modal.classList.remove("hidden");
        document.body.classList.add("overflow-hidden");
    }

    function closeModal() {
        els.modal.classList.add("hidden");
        document.body.classList.remove("overflow-hidden");
        els.form.reset();
        els.id.value = "";
        clearFormErrors();
        syncMaxDiscountState();
    }

    function syncMaxDiscountState() {
        const isFixedAmount = els.discountType.value === "FIXED_AMOUNT";
        els.maxDiscount.disabled = isFixedAmount;
        if (isFixedAmount) {
            els.maxDiscount.value = "";
        }
    }

    function openCreateModal() {
        clearFormErrors();
        els.form.reset();
        els.id.value = "";
        els.modalTitle.textContent = "Tạo voucher";
        els.submitBtn.textContent = "Tạo voucher";
        syncMaxDiscountState();
        openModal();
    }

    function openEditModal(voucher) {
        clearFormErrors();
        els.form.reset();
        els.id.value = voucher.id;
        els.modalTitle.textContent = "Cập nhật voucher";
        els.submitBtn.textContent = "Lưu thay đổi";
        els.name.value = voucher.name || "";
        els.code.value = voucher.code || "";
        els.description.value = voucher.description || "";
        els.discountType.value = voucher.discount_type || "PERCENTAGE";
        els.discountValue.value = voucher.discount_value ?? "";
        els.minimumOrder.value = voucher.minimum_order ?? 0;
        els.maxDiscount.value = voucher.max_discount ?? "";
        els.usageLimit.value = voucher.usage_limit ?? 1;
        els.startDate.value = toDatetimeLocalValue(voucher.start_date);
        els.endDate.value = toDatetimeLocalValue(voucher.end_date);
        syncMaxDiscountState();
        openModal();
    }

    function collectPayload() {
        return {
            name: els.name.value.trim(),
            code: els.code.value.trim(),
            description: els.description.value.trim(),
            discount_type: els.discountType.value,
            discount_value: Number(els.discountValue.value),
            minimum_order: Number(els.minimumOrder.value || 0),
            max_discount: els.maxDiscount.value ? Number(els.maxDiscount.value) : null,
            usage_limit: Number(els.usageLimit.value || 0),
            start_date: els.startDate.value,
            end_date: els.endDate.value,
        };
    }

    function validateForm(payload) {
        clearFormErrors();
        let valid = true;

        if (!payload.name) {
            setFieldError("voucher-name", "Tên voucher không được để trống");
            valid = false;
        }
        if (!payload.code) {
            setFieldError("voucher-code", "Mã voucher không được để trống");
            valid = false;
        }
        if (!payload.discount_type) {
            setFieldError("voucher-discount-type", "Loại giảm là bắt buộc");
            valid = false;
        }
        if (!(payload.discount_value > 0)) {
            setFieldError("voucher-discount-value", "Giá trị giảm phải lớn hơn 0");
            valid = false;
        }
        if (!(payload.minimum_order >= 0)) {
            setFieldError("voucher-minimum-order", "Đơn tối thiểu không được âm");
            valid = false;
        }
        if (!(payload.usage_limit >= 1)) {
            setFieldError("voucher-usage-limit", "Giới hạn lượt dùng phải lớn hơn hoặc bằng 1");
            valid = false;
        }
        if (!payload.start_date) {
            setFieldError("voucher-start-date", "Ngày bắt đầu là bắt buộc");
            valid = false;
        }
        if (!payload.end_date) {
            setFieldError("voucher-end-date", "Ngày kết thúc là bắt buộc");
            valid = false;
        }

        const startDate = payload.start_date ? new Date(payload.start_date) : null;
        const endDate = payload.end_date ? new Date(payload.end_date) : null;
        if (startDate && endDate && startDate >= endDate) {
            setFieldError("voucher-end-date", "Ngày kết thúc phải lớn hơn ngày bắt đầu");
            valid = false;
        }

        if (payload.discount_type === "PERCENTAGE" && payload.discount_value > 100) {
            setFieldError("voucher-discount-value", "Voucher phần trăm không được vượt quá 100");
            valid = false;
        }

        if (payload.discount_type === "FIXED_AMOUNT") {
            payload.max_discount = null;
        }

        return valid;
    }

    async function submitForm(event) {
        event.preventDefault();

        const voucherId = els.id.value.trim();
        const payload = collectPayload();
        if (!validateForm(payload)) {
            setFormError("Vui lòng kiểm tra lại các trường dữ liệu.");
            return;
        }

        const originalText = els.submitBtn.textContent;
        els.submitBtn.disabled = true;
        els.submitBtn.textContent = "Đang lưu...";

        try {
            const res = await fetch(voucherId ? `${API_URL}/${voucherId}` : API_URL, {
                method: voucherId ? "PUT" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.message || "Lưu voucher thất bại");
            }

            closeModal();
            await loadVouchers();
        } catch (err) {
            setFormError(err.message || "Lỗi kết nối máy chủ");
        } finally {
            els.submitBtn.disabled = false;
            els.submitBtn.textContent = originalText;
        }
    }

    async function deleteVoucher(voucherId) {
        if (!confirm("Xác nhận xóa voucher này?")) return;

        try {
            const res = await fetch(`${API_URL}/${voucherId}`, {
                method: "DELETE",
            });
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.message || "Xóa voucher thất bại");
            }

            await loadVouchers();
        } catch (err) {
            alert(err.message || "Lỗi kết nối máy chủ");
        }
    }

    document.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button) return;

        const action = button.dataset.action;
        const voucherId = Number(button.dataset.id);
        const voucher = state.vouchers.find((item) => item.id === voucherId);

        if (action === "edit" && voucher) {
            openEditModal(voucher);
        }

        if (action === "delete") {
            deleteVoucher(voucherId);
        }
    });

    els.openCreateBtn?.addEventListener("click", openCreateModal);
    els.refreshBtn?.addEventListener("click", loadVouchers);
    els.closeModalBtn?.addEventListener("click", closeModal);
    els.cancelBtn?.addEventListener("click", closeModal);
    els.backdrop?.addEventListener("click", closeModal);
    els.form?.addEventListener("submit", submitForm);
    els.search?.addEventListener("input", applyFilter);
    els.discountType?.addEventListener("change", syncMaxDiscountState);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !els.modal.classList.contains("hidden")) {
            closeModal();
        }
    });

    syncMaxDiscountState();
    loadVouchers();
})();
