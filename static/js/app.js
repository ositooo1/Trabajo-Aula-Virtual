function getToken() {
    return localStorage.getItem('token');
}

function getUser() {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

function showModal(titulo, contenido) {
    document.getElementById('modalTitle').textContent = titulo;
    document.getElementById('modalBody').innerHTML = contenido;
    document.getElementById('modalBg').classList.add('active');
}

function closeModal() {
    document.getElementById('modalBg').classList.remove('active');
}

function showAlert(msg, tipo) {
    const d = document.createElement('div');
    d.className = 'msg msg-' + tipo;
    d.textContent = msg;
    const c = document.getElementById('alerts');
    if (c) {
        c.appendChild(d);
        setTimeout(() => d.remove(), 3000);
    }
}

async function api(endpoint, method, data) {
    const config = {
        method: method || 'GET',
        headers: { 'Content-Type': 'application/json' }
    };
    if (getToken()) {
        config.headers['Authorization'] = 'Bearer ' + getToken();
    }
    if (data) config.body = JSON.stringify(data);

    const res = await fetch('/api' + endpoint, config);
    if (res.status === 401) { logout(); return null; }
    const json = await res.json();
    if (!res.ok) { showAlert(json.message || 'Error', 'error'); return null; }
    return json;
}
