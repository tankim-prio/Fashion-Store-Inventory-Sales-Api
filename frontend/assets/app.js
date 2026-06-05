const API_BASE = "";

function getToken() {
    return localStorage.getItem("access_token");
}

function setToken(token) {
    localStorage.setItem("access_token", token);
}

function clearToken() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_role");
}

function showError(message) {
    const errorBox = document.getElementById("errorBox");
    if (errorBox) {
        errorBox.style.display = "block";
        errorBox.innerText = message;
    }
}

async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Login failed");
    }

    setToken(data.access_token);
    localStorage.setItem("user_email", data.user.email);
    localStorage.setItem("user_role", data.user.role);

    window.location.href = "/site/dashboard.html";
}

async function apiGet(path) {
    const token = getToken();

    const response = await fetch(path, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Request failed");
    }

    return data;
}

function logout() {
    clearToken();
    window.location.href = "/site/login.html";
}

async function loadMe() {
    const token = getToken();

    if (!token) {
        window.location.href = "/site/login.html";
        return;
    }

    try {
        const user = await apiGet("/auth/me");

        const accountInfo = document.getElementById("accountInfo");
        if (accountInfo) {
            accountInfo.innerText = `${user.email} (${user.role})`;
        }
    } catch (error) {
        clearToken();
        window.location.href = "/site/login.html";
    }
}

function renderTable(data) {
    if (!Array.isArray(data)) {
        data = [data];
    }

    if (data.length === 0) {
        return "<p>No data found.</p>";
    }

    const keys = Object.keys(data[0]);

    let html = "<table><thead><tr>";

    keys.forEach(key => {
        html += `<th>${key}</th>`;
    });

    html += "</tr></thead><tbody>";

    data.forEach(row => {
        html += "<tr>";
        keys.forEach(key => {
            let value = row[key];

            if (typeof value === "object" && value !== null) {
                value = JSON.stringify(value);
            }

            html += `<td>${value ?? ""}</td>`;
        });
        html += "</tr>";
    });

    html += "</tbody></table>";
    return html;
}

async function loadSection(section) {
    const title = document.getElementById("sectionTitle");
    const content = document.getElementById("contentArea");

    if (!title || !content) return;

    title.innerText = section.toUpperCase();
    content.innerHTML = "Loading...";

    const routes = {
        products: "/products/",
        categories: "/categories/",
        variants: "/variants/",
        stock: "/stock/history",
        customers: "/customers/",
        orders: "/orders/",
        payments: "/payments/",
        invoices: "/invoices/",
        reports: "/reports/profit",
        users: "/users/"
    };

    try {
        const data = await apiGet(routes[section]);
        content.innerHTML = renderTable(data);
    } catch (error) {
        content.innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                await login(email, password);
            } catch (error) {
                showError(error.message);
            }
        });
    }

    if (window.location.pathname.includes("dashboard.html")) {
        loadMe();
    }
});
