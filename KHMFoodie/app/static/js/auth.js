// Password toggle
document.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const span = btn.querySelector('.material-symbols-outlined');
        if (span && span.innerText === 'visibility') {
            span.innerText = 'visibility_off';
            const input = btn.previousElementSibling;
            if (input) input.type = 'text';
        } else if (span && span.innerText === 'visibility_off') {
            span.innerText = 'visibility';
            const input = btn.previousElementSibling;
            if (input) input.type = 'password';
        }
    });
});

// Login form
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const username = document.getElementById('identity').value.trim();
    const password = document.getElementById('password').value.trim();
    const remember = document.querySelector('input[type="checkbox"]')?.checked || false;

    if (!username || !password) {
        alert('Vui lòng nhập username và mật khẩu');
        return;
    }

    const originalText = btn.innerText;
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span>';
    btn.disabled = true;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, remember })
        });
        const data = await res.json();
        if (res.ok) {
            window.location.href = data.redirect || '/';
        } else {
            alert(data.message || 'Đăng nhập thất bại');
        }
    } catch (err) {
        alert('Lỗi kết nối đến máy chủ');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
});

// Register form
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const data = {
        name: document.getElementById('full_name').value.trim(),
        username: document.getElementById('username').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        password: document.getElementById('password').value.trim(),
        confirm_password: document.getElementById('confirm_password').value.trim(),
    };

    if (!data.name || !data.username || !data.email || !data.phone || !data.password || !data.confirm_password) {
        alert('Vui lòng điền đầy đủ thông tin');
        return;
    }

    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span> Đang xử lý...';

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (res.ok) {
            window.location.href = '/login';
        } else {
            alert(result.message || 'Đăng ký thất bại');
        }
    } catch (err) {
        alert('Lỗi kết nối đến máy chủ');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});
