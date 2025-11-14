// Базовый URL API сервера
const API_BASE = "http://localhost:3000/api";

// ------------------ UTILS ------------------

async function apiGet(path) {
    const resp = await fetch(API_BASE + path, {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" }
    });

    if (!resp.ok) {
        throw new Error(`GET ${path} failed (${resp.status})`);
    }

    return resp.json();
}

async function apiPost(path, data = {}) {
    const resp = await fetch(API_BASE + path, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!resp.ok) {
        throw new Error(`POST ${path} failed (${resp.status})`);
    }

    return resp.json();
}

async function apiDelete(path) {
    const resp = await fetch(API_BASE + path, {
        method: "DELETE",
        credentials: "include",
    });

    if (!resp.ok) {
        throw new Error(`DELETE ${path} failed (${resp.status})`);
    }

    return true;
}

// ------------------ EXPORTS ------------------
window.apiGet = apiGet;
window.apiPost = apiPost;
window.apiDelete = apiDelete;
