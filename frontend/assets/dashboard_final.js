let currentUser = null;
let categoryCache = [];
let productCache = [];
let variantCache = [];
let customerCache = [];
let userCache = [];
let currentInvoiceData = null;

function getToken() {
    return localStorage.getItem("access_token");
}

function setToken(token) {
    localStorage.setItem("access_token", token);
}

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_role");
    window.location.href = "/site/login.html";
}

function formatApiError(data) {
    if (!data) return "Request failed";

    if (data.message) {
        if (Array.isArray(data.errors) && data.errors.length > 0) {
            const firstError = data.errors[0];
            if (firstError.field && firstError.message) {
                return `${data.message}: ${firstError.field} - ${firstError.message}`;
            }
        }
        return data.message;
    }

    if (typeof data.detail === "string") return data.detail;

    if (Array.isArray(data.detail) && data.detail.length > 0) {
        const firstError = data.detail[0];
        if (firstError.loc && firstError.msg) {
            return `${firstError.loc.join(".")} - ${firstError.msg}`;
        }
    }

    return "Request failed";
}

async function apiGet(url) {
    const response = await fetch(url, {
        headers: {
            "Authorization": `Bearer ${getToken()}`
        }
    });

    let data = null;
    try { data = await response.json(); } catch {}

    if (!response.ok) {
        throw new Error(formatApiError(data));
    }

    return data;
}

async function apiPost(url, body) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${getToken()}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });

    let data = null;
    try { data = await response.json(); } catch {}

    if (!response.ok) {
        throw new Error(formatApiError(data));
    }

    return data;
}

async function apiPut(url, body) {
    const response = await fetch(url, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${getToken()}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });

    let data = null;
    try { data = await response.json(); } catch {}

    if (!response.ok) {
        throw new Error(formatApiError(data));
    }

    return data;
}

async function apiDelete(url) {
    const response = await fetch(url, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${getToken()}`
        }
    });

    let data = null;
    try { data = await response.json(); } catch {}

    if (!response.ok) {
        throw new Error(formatApiError(data));
    }

    return data;
}

function setPage(title, subtitle) {
    document.getElementById("pageTitle").innerText = title;
    document.getElementById("pageSubtitle").innerText = subtitle;
}

function setContent(html) {
    document.getElementById("mainContent").innerHTML = html;
}

function showMessage(message, type = "success") {
    const box = document.getElementById("messageBox");
    if (!box) return;

    box.className = type === "success" ? "message success" : "message error";
    box.innerText = message;
    box.style.display = "block";
}

function showProfileMessage(message, type = "success") {
    const box = document.getElementById("profileMessage");
    if (!box) return;

    box.className = type === "success" ? "profile-message success" : "profile-message error";
    box.innerText = message;
}

function money(value) {
    const num = Number(value || 0);
    return num.toFixed(2);
}

function getBadge(value) {
    if (value === true) return `<span class="badge badge-green">active</span>`;
    if (value === false) return `<span class="badge badge-red">inactive</span>`;

    const text = String(value || "").toLowerCase();

    if (["paid", "admin", "active"].includes(text)) {
        return `<span class="badge badge-green">${value}</span>`;
    }

    if (["pending", "staff"].includes(text)) {
        return `<span class="badge badge-yellow">${value}</span>`;
    }

    if (["failed", "cancelled", "refunded", "inactive"].includes(text)) {
        return `<span class="badge badge-red">${value}</span>`;
    }

    return value ?? "";
}

function formatCell(key, value) {
    if (value === null || value === undefined) return "";

    if (key.includes("status") || key === "role" || key === "is_active") {
        return getBadge(value);
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return value;
}

function renderTable(data) {
    if (!Array.isArray(data)) data = [data];

    if (data.length === 0) return "<p>No data found.</p>";

    const keys = Object.keys(data[0]);

    let html = `<div class="table-wrapper"><table><thead><tr>`;

    keys.forEach(key => {
        html += `<th>${key}</th>`;
    });

    html += `</tr></thead><tbody>`;

    data.forEach(row => {
        html += `<tr>`;

        keys.forEach(key => {
            html += `<td>${formatCell(key, row[key])}</td>`;
        });

        html += `</tr>`;
    });

    html += `</tbody></table></div>`;
    return html;
}

function toggleMobileMenu() {
    document.getElementById("profilePanel").classList.remove("open");
    document.getElementById("mobileMenu").classList.toggle("open");
}

function closeMobileMenu() {
    document.getElementById("mobileMenu").classList.remove("open");
}

function toggleProfilePanel() {
    document.getElementById("mobileMenu").classList.remove("open");
    document.getElementById("profilePanel").classList.toggle("open");
}

function closeProfilePanel() {
    document.getElementById("profilePanel").classList.remove("open");
}

document.addEventListener("click", function(event) {
    const mobileMenu = document.getElementById("mobileMenu");
    const profilePanel = document.getElementById("profilePanel");
    const menuButton = document.querySelector(".mobile-menu-btn");
    const profileButton = document.querySelector(".profile-btn");

    const insideMenu = mobileMenu.contains(event.target);
    const insideProfile = profilePanel.contains(event.target);
    const clickedMenuButton = menuButton.contains(event.target);
    const clickedProfileButton = profileButton.contains(event.target);

    if (!insideMenu && !clickedMenuButton) closeMobileMenu();
    if (!insideProfile && !clickedProfileButton) closeProfilePanel();
});

function fillProfile(user) {
    document.getElementById("profileDisplayName").innerText = user.full_name || "Account";
    document.getElementById("profileDisplayRole").innerText = `${user.email} • ${user.role}`;
    document.getElementById("profileName").value = user.full_name || "";
    document.getElementById("profileEmail").value = user.email || "";
    document.getElementById("profilePhone").value = user.phone || "";

    document.querySelectorAll(".profile-avatar").forEach(item => {
        item.innerText = user.email ? user.email[0].toUpperCase() : "A";
    });
}

async function loadMe() {
    if (!getToken()) {
        window.location.href = "/site/login.html";
        return;
    }

    try {
        const user = await apiGet("/auth/me");
        currentUser = user;

        document.body.dataset.role = user.role;

        localStorage.setItem("user_email", user.email);
        localStorage.setItem("user_role", user.role);

        fillProfile(user);

    } catch (error) {
        logout();
    }
}

async function saveProfile() {
    try {
        const data = await apiPut("/auth/profile", {
            full_name: document.getElementById("profileName").value,
            email: document.getElementById("profileEmail").value,
            phone: document.getElementById("profilePhone").value || null
        });

        setToken(data.access_token);
        currentUser = data.user;
        fillProfile(data.user);
        showProfileMessage("Profile updated successfully");

    } catch (error) {
        showProfileMessage(error.message, "error");
    }
}

async function deactivateMyAccount() {
    const ok = confirm("Are you sure? Your account will be deactivated and you will be logged out.");
    if (!ok) return;

    try {
        await apiDelete("/auth/profile");
        alert("Your account has been deactivated.");
        logout();
    } catch (error) {
        showProfileMessage(error.message, "error");
    }
}

function loadDashboard() {
    closeMobileMenu();
    setPage("Dashboard", "Business overview, stock health, sales summary and recent activity.");

    setContent(`
        <div class="cards">
            <div class="card" onclick="loadCategoriesPage()"><h3>Categories</h3><p>Create and view categories.</p></div>
            <div class="card" onclick="loadProductsPage()"><h3>Products</h3><p>Create and search products.</p></div>
            <div class="card" onclick="loadVariantsPage()"><h3>Variants</h3><p>Create product variants.</p></div>
            <div class="card" onclick="loadStockPage()"><h3>Stock</h3><p>Add, remove and monitor stock.</p></div>
            <div class="card" onclick="loadCustomersPage()"><h3>Customers</h3><p>Create and manage customers.</p></div>
            <div class="card" onclick="loadOrdersPage()"><h3>Orders</h3><p>Create customer orders.</p></div>
            <div class="card" onclick="loadPaymentsPage()"><h3>Payments</h3><p>Receive order payments.</p></div>
            <div class="card" onclick="loadInvoicesPage()"><h3>Invoices</h3><p>Generate and print invoices.</p></div>
            <div class="card" onclick="loadReportsPage()"><h3>Reports</h3><p>View sales and stock reports.</p></div>
            <div class="card admin-only" onclick="loadUsersPage()"><h3>Users</h3><p>Admin user management.</p></div>
        </div>

        <div class="stats-grid">
            <div class="stat-card"><h3>Total Products</h3><div id="statProducts" class="stat-number">...</div></div>
            <div class="stat-card"><h3>Total Stock</h3><div id="statStock" class="stat-number">...</div></div>
            <div class="stat-card"><h3>Total Orders</h3><div id="statOrders" class="stat-number">...</div></div>
            <div class="stat-card"><h3>Total Profit</h3><div id="statProfit" class="stat-number">...</div></div>
        </div>

        <div class="dashboard-row">
            <div class="content-box">
                <h2>Recent Orders</h2>
                <div id="recentOrdersTable">Loading...</div>
            </div>

            <div class="content-box">
                <h2>Low Stock Preview</h2>
                <div id="dashboardLowStockTable">Loading...</div>
            </div>
        </div>
    `);

    refreshDashboardStats();
}

async function refreshDashboardStats() {
    try {
        const products = await apiGet("/products/");
        const variants = await apiGet("/variants/");
        const orders = await apiGet("/orders/");
        const profit = await apiGet("/reports/profit");

        const totalStock = variants.reduce((sum, item) => sum + Number(item.stock_quantity || 0), 0);
        const lowStock = variants.filter(item => Number(item.stock_quantity || 0) <= 5);

        document.getElementById("statProducts").innerText = products.length;
        document.getElementById("statStock").innerText = totalStock;
        document.getElementById("statOrders").innerText = orders.length;
        document.getElementById("statProfit").innerText = money(profit.total_profit || profit.profit || 0);

        document.getElementById("recentOrdersTable").innerHTML = renderTable(orders.slice(-5).reverse());
        document.getElementById("dashboardLowStockTable").innerHTML = renderTable(lowStock.slice(0, 5));
    } catch (error) {
        document.getElementById("recentOrdersTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadCategoriesPage() {
    closeMobileMenu();
    setPage("Categories", "Create, view, edit and delete categories.");

    setContent(`
        <div class="content-box">
            <h2>Create Category</h2>
            <div id="messageBox" class="message"></div>

            <form id="categoryForm" class="form-grid">
                <input id="categoryName" type="text" placeholder="Category name" required>
                <input id="categoryDescription" type="text" placeholder="Description">
                <button type="submit">Create Category</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Category List</h2>
            <div id="categoryTable">Loading...</div>
        </div>
    `);

    document.getElementById("categoryForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/categories/", {
                name: document.getElementById("categoryName").value,
                description: document.getElementById("categoryDescription").value || null
            });

            showMessage("Category created successfully");
            document.getElementById("categoryForm").reset();
            refreshCategories();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshCategories();
}

async function refreshCategories() {
    try {
        categoryCache = await apiGet("/categories/");

        let html = `<div class="table-wrapper"><table><thead><tr>
            <th>ID</th><th>Name</th><th>Description</th><th>Actions</th>
        </tr></thead><tbody>`;

        categoryCache.forEach(item => {
            html += `<tr>
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.description || ""}</td>
                <td>
                    <button class="small-btn" onclick="editCategory(${item.id})">Edit</button>
                    <button class="small-btn danger" onclick="deleteCategory(${item.id})">Delete</button>
                </td>
            </tr>`;
        });

        html += `</tbody></table></div>`;
        document.getElementById("categoryTable").innerHTML = categoryCache.length ? html : "<p>No category found.</p>";
    } catch (error) {
        document.getElementById("categoryTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editCategory(id) {
    const item = categoryCache.find(x => x.id === id);
    if (!item) return;

    const name = prompt("Category name:", item.name);
    if (!name) return;

    const description = prompt("Description:", item.description || "");

    try {
        await apiPut(`/categories/${id}`, { name, description: description || null });
        showMessage("Category updated successfully");
        refreshCategories();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteCategory(id) {
    if (!confirm("Delete this category?")) return;

    try {
        await apiDelete(`/categories/${id}`);
        showMessage("Category deleted successfully");
        refreshCategories();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function loadProductsPage() {
    closeMobileMenu();
    setPage("Products", "Create, search, edit and delete products.");

    setContent(`
        <div class="content-box">
            <h2>Create Product</h2>
            <div id="messageBox" class="message"></div>

            <form id="productForm" class="form-grid">
                <input id="productName" type="text" placeholder="Product name" required>
                <select id="productCategory" required><option value="">Select category</option></select>
                <input id="productBrand" type="text" placeholder="Brand">
                <input id="productDescription" type="text" placeholder="Description">
                <button type="submit">Create Product</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Search Products</h2>
            <div class="form-grid">
                <input id="productSearch" type="text" placeholder="Search product">
                <button onclick="searchProducts()">Search</button>
                <button onclick="refreshProducts()">Show All</button>
            </div>
        </div>

        <div class="content-box">
            <h2>Product List</h2>
            <div id="productTable">Loading...</div>
        </div>
    `);

    await loadCategoryDropdown("productCategory");

    document.getElementById("productForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/products/", {
                name: document.getElementById("productName").value,
                category_id: Number(document.getElementById("productCategory").value),
                brand: document.getElementById("productBrand").value || null,
                description: document.getElementById("productDescription").value || null
            });

            showMessage("Product created successfully");
            document.getElementById("productForm").reset();
            refreshProducts();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshProducts();
}

async function loadCategoryDropdown(selectId) {
    const select = document.getElementById(selectId);
    const categories = await apiGet("/categories/");

    categories.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.innerText = `${item.id} - ${item.name}`;
        select.appendChild(option);
    });
}

async function refreshProducts() {
    try {
        productCache = await apiGet("/products/");
        renderProductTable(productCache);
    } catch (error) {
        document.getElementById("productTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function searchProducts() {
    const q = document.getElementById("productSearch").value;

    try {
        const data = await apiGet(`/products/?search=${encodeURIComponent(q)}`);
        renderProductTable(data);
    } catch (error) {
        document.getElementById("productTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

function renderProductTable(data) {
    if (!data.length) {
        document.getElementById("productTable").innerHTML = "<p>No product found.</p>";
        return;
    }

    let html = `<div class="table-wrapper"><table><thead><tr>
        <th>ID</th><th>Name</th><th>Category</th><th>Brand</th><th>Description</th><th>Active</th><th>Actions</th>
    </tr></thead><tbody>`;

    data.forEach(item => {
        html += `<tr>
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.category_id}</td>
            <td>${item.brand || ""}</td>
            <td>${item.description || ""}</td>
            <td>${getBadge(item.is_active)}</td>
            <td>
                <button class="small-btn" onclick="editProduct(${item.id})">Edit</button>
                <button class="small-btn danger" onclick="deleteProduct(${item.id})">Delete</button>
            </td>
        </tr>`;
    });

    html += `</tbody></table></div>`;
    document.getElementById("productTable").innerHTML = html;
}

async function editProduct(id) {
    const item = productCache.find(x => x.id === id);
    if (!item) return;

    const name = prompt("Product name:", item.name);
    if (!name) return;

    const category_id = prompt("Category ID:", item.category_id);
    if (!category_id) return;

    const brand = prompt("Brand:", item.brand || "");
    const description = prompt("Description:", item.description || "");

    try {
        await apiPut(`/products/${id}`, {
            name,
            category_id: Number(category_id),
            brand: brand || null,
            description: description || null
        });

        showMessage("Product updated successfully");
        refreshProducts();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteProduct(id) {
    if (!confirm("Delete this product?")) return;

    try {
        await apiDelete(`/products/${id}`);
        showMessage("Product deleted successfully");
        refreshProducts();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function loadVariantsPage() {
    closeMobileMenu();
    setPage("Variants", "Create, edit and delete product variants.");

    setContent(`
        <div class="content-box">
            <h2>Create Variant</h2>
            <div id="messageBox" class="message"></div>

            <form id="variantForm" class="form-grid">
                <select id="variantProduct" required><option value="">Select product</option></select>
                <input id="variantSize" type="text" placeholder="Size" required>
                <input id="variantColor" type="text" placeholder="Color" required>
                <input id="variantBuyPrice" type="number" placeholder="Buy price" required>
                <input id="variantSellPrice" type="number" placeholder="Sell price" required>
                <input id="variantStock" type="number" placeholder="Stock quantity" required>
                <input id="variantSku" type="text" placeholder="SKU" required>
                <button type="submit">Create Variant</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Variant List</h2>
            <div id="variantTable">Loading...</div>
        </div>
    `);

    await loadProductDropdown("variantProduct");

    document.getElementById("variantForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/variants/", {
                product_id: Number(document.getElementById("variantProduct").value),
                size: document.getElementById("variantSize").value,
                color: document.getElementById("variantColor").value,
                buy_price: Number(document.getElementById("variantBuyPrice").value),
                sell_price: Number(document.getElementById("variantSellPrice").value),
                stock_quantity: Number(document.getElementById("variantStock").value),
                sku: document.getElementById("variantSku").value
            });

            showMessage("Variant created successfully");
            document.getElementById("variantForm").reset();
            refreshVariants();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshVariants();
}

async function loadProductDropdown(selectId) {
    const select = document.getElementById(selectId);
    const products = await apiGet("/products/");

    products.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.innerText = `${item.id} - ${item.name}`;
        select.appendChild(option);
    });
}

async function refreshVariants() {
    try {
        variantCache = await apiGet("/variants/");

        let html = `<div class="table-wrapper"><table><thead><tr>
            <th>ID</th><th>Product</th><th>Size</th><th>Color</th><th>Buy</th><th>Sell</th><th>Stock</th><th>SKU</th><th>Actions</th>
        </tr></thead><tbody>`;

        variantCache.forEach(item => {
            html += `<tr>
                <td>${item.id}</td>
                <td>${item.product_id}</td>
                <td>${item.size}</td>
                <td>${item.color}</td>
                <td>${item.buy_price}</td>
                <td>${item.sell_price}</td>
                <td>${item.stock_quantity}</td>
                <td>${item.sku}</td>
                <td>
                    <button class="small-btn" onclick="editVariant(${item.id})">Edit</button>
                    <button class="small-btn danger" onclick="deleteVariant(${item.id})">Delete</button>
                </td>
            </tr>`;
        });

        html += `</tbody></table></div>`;
        document.getElementById("variantTable").innerHTML = variantCache.length ? html : "<p>No variant found.</p>";
    } catch (error) {
        document.getElementById("variantTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editVariant(id) {
    const item = variantCache.find(x => x.id === id);
    if (!item) return;

    const product_id = prompt("Product ID:", item.product_id);
    const size = prompt("Size:", item.size);
    const color = prompt("Color:", item.color);
    const buy_price = prompt("Buy price:", item.buy_price);
    const sell_price = prompt("Sell price:", item.sell_price);
    const stock_quantity = prompt("Stock quantity:", item.stock_quantity);
    const sku = prompt("SKU:", item.sku);

    if (!product_id || !size || !color || !buy_price || !sell_price || !stock_quantity || !sku) return;

    try {
        await apiPut(`/variants/${id}`, {
            product_id: Number(product_id),
            size,
            color,
            buy_price: Number(buy_price),
            sell_price: Number(sell_price),
            stock_quantity: Number(stock_quantity),
            sku
        });

        showMessage("Variant updated successfully");
        refreshVariants();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteVariant(id) {
    if (!confirm("Delete this variant?")) return;

    try {
        await apiDelete(`/variants/${id}`);
        showMessage("Variant deleted successfully");
        refreshVariants();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function loadStockPage() {
    closeMobileMenu();
    setPage("Stock Management", "Add stock, remove stock and view stock history.");

    setContent(`
        <div class="content-box">
            <h2>Current Variant Stock</h2>
            <div id="variantStockTable">Loading...</div>
        </div>

        <div class="content-box">
            <h2>Add Stock</h2>
            <div id="messageBox" class="message"></div>

            <form id="addStockForm" class="form-grid">
                <select id="addStockVariant" required><option value="">Select variant</option></select>
                <input id="addStockQuantity" type="number" placeholder="Quantity to add" required>
                <input id="addStockNote" type="text" placeholder="Note">
                <button type="submit">Add Stock</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Remove Stock</h2>

            <form id="removeStockForm" class="form-grid">
                <select id="removeStockVariant" required><option value="">Select variant</option></select>
                <input id="removeStockQuantity" type="number" placeholder="Quantity to remove" required>
                <input id="removeStockNote" type="text" placeholder="Note">
                <button type="submit">Remove Stock</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Stock History</h2>
            <div id="stockHistoryTable">Loading...</div>
        </div>

        <div class="content-box">
            <h2>Low Stock</h2>
            <div class="form-grid">
                <input id="lowStockLimit" type="number" value="5">
                <button onclick="refreshLowStock()">Check Low Stock</button>
            </div>
            <div id="lowStockTable">Choose limit and check low stock.</div>
        </div>
    `);

    await loadStockDropdowns();

    document.getElementById("addStockForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/stock/add", {
                variant_id: Number(document.getElementById("addStockVariant").value),
                quantity: Number(document.getElementById("addStockQuantity").value),
                note: document.getElementById("addStockNote").value || null,
                created_by: localStorage.getItem("user_email")
            });

            showMessage("Stock added successfully");
            refreshVariantStock();
            refreshStockHistory();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    document.getElementById("removeStockForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/stock/remove", {
                variant_id: Number(document.getElementById("removeStockVariant").value),
                quantity: Number(document.getElementById("removeStockQuantity").value),
                note: document.getElementById("removeStockNote").value || null,
                created_by: localStorage.getItem("user_email")
            });

            showMessage("Stock removed successfully");
            refreshVariantStock();
            refreshStockHistory();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshVariantStock();
    refreshStockHistory();
}

async function loadStockDropdowns() {
    const variants = await apiGet("/variants/");

    ["addStockVariant", "removeStockVariant"].forEach(id => {
        const select = document.getElementById(id);

        variants.forEach(item => {
            const option = document.createElement("option");
            option.value = item.id;
            option.innerText = `${item.id} - ${item.sku} | Stock: ${item.stock_quantity}`;
            select.appendChild(option);
        });
    });
}

async function refreshVariantStock() {
    try {
        const variants = await apiGet("/variants/");
        document.getElementById("variantStockTable").innerHTML = renderTable(variants);
    } catch (error) {
        document.getElementById("variantStockTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function refreshStockHistory() {
    try {
        const data = await apiGet("/stock/history");
        document.getElementById("stockHistoryTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("stockHistoryTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function refreshLowStock() {
    const limit = document.getElementById("lowStockLimit").value || 5;

    try {
        const data = await apiGet(`/stock/low?threshold=${limit}`);
        document.getElementById("lowStockTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("lowStockTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadCustomersPage() {
    closeMobileMenu();
    setPage("Customers", "Create, search, edit and delete customers.");

    setContent(`
        <div class="content-box">
            <h2>Create Customer</h2>
            <div id="messageBox" class="message"></div>

            <form id="customerForm" class="form-grid">
                <input id="customerName" type="text" placeholder="Customer name" required>
                <input id="customerPhone" type="text" placeholder="Phone" required>
                <input id="customerEmail" type="email" placeholder="Email">
                <input id="customerAddress" type="text" placeholder="Address">
                <button type="submit">Create Customer</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Search Customers</h2>
            <div class="form-grid">
                <input id="customerSearch" type="text" placeholder="Search customer">
                <button onclick="searchCustomers()">Search</button>
                <button onclick="refreshCustomers()">Show All</button>
            </div>
        </div>

        <div class="content-box">
            <h2>Customer List</h2>
            <div id="customerTable">Loading...</div>
        </div>
    `);

    document.getElementById("customerForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/customers/", {
                name: document.getElementById("customerName").value,
                phone: document.getElementById("customerPhone").value,
                email: document.getElementById("customerEmail").value || null,
                address: document.getElementById("customerAddress").value || null
            });

            showMessage("Customer created successfully");
            document.getElementById("customerForm").reset();
            refreshCustomers();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshCustomers();
}

async function refreshCustomers() {
    try {
        customerCache = await apiGet("/customers/");
        renderCustomerTable(customerCache);
    } catch (error) {
        document.getElementById("customerTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function searchCustomers() {
    const q = document.getElementById("customerSearch").value;

    try {
        const data = await apiGet(`/customers/?search=${encodeURIComponent(q)}`);
        renderCustomerTable(data);
    } catch (error) {
        document.getElementById("customerTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

function renderCustomerTable(data) {
    if (!data.length) {
        document.getElementById("customerTable").innerHTML = "<p>No customer found.</p>";
        return;
    }

    let html = `<div class="table-wrapper"><table><thead><tr>
        <th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Address</th><th>Active</th><th>Actions</th>
    </tr></thead><tbody>`;

    data.forEach(item => {
        html += `<tr>
            <td>${item.id}</td><td>${item.name}</td><td>${item.phone}</td><td>${item.email || ""}</td><td>${item.address || ""}</td><td>${getBadge(item.is_active)}</td>
            <td>
                <button class="small-btn" onclick="editCustomer(${item.id})">Edit</button>
                <button class="small-btn danger" onclick="deleteCustomer(${item.id})">Delete</button>
            </td>
        </tr>`;
    });

    html += `</tbody></table></div>`;
    document.getElementById("customerTable").innerHTML = html;
}

async function editCustomer(id) {
    const item = customerCache.find(x => x.id === id);
    if (!item) return;

    const name = prompt("Name:", item.name);
    const phone = prompt("Phone:", item.phone);
    const email = prompt("Email:", item.email || "");
    const address = prompt("Address:", item.address || "");

    if (!name || !phone) return;

    try {
        await apiPut(`/customers/${id}`, {
            name,
            phone,
            email: email || null,
            address: address || null
        });

        showMessage("Customer updated successfully");
        refreshCustomers();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteCustomer(id) {
    if (!confirm("Delete this customer?")) return;

    try {
        await apiDelete(`/customers/${id}`);
        showMessage("Customer deleted successfully");
        refreshCustomers();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function loadOrdersPage() {
    closeMobileMenu();
    setPage("Orders", "Create orders and filter order list.");

    setContent(`
        <div class="content-box">
            <h2>Create Order</h2>
            <div id="messageBox" class="message"></div>

            <form id="orderForm" class="form-grid">
                <select id="orderCustomer" required><option value="">Select customer</option></select>
                <select id="orderVariant" required><option value="">Select variant</option></select>
                <input id="orderQuantity" type="number" placeholder="Quantity" required>
                <input id="orderDiscount" type="number" placeholder="Discount" value="0">
                <button type="submit">Create Order</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Order List</h2>
            <div id="orderTable">Loading...</div>
        </div>
    `);

    await loadCustomerDropdown("orderCustomer");
    await loadVariantDropdown("orderVariant");

    document.getElementById("orderForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/orders/", {
                customer_id: Number(document.getElementById("orderCustomer").value),
                items: [
                    {
                        variant_id: Number(document.getElementById("orderVariant").value),
                        quantity: Number(document.getElementById("orderQuantity").value)
                    }
                ],
                discount: Number(document.getElementById("orderDiscount").value || 0),
                created_by: localStorage.getItem("user_email")
            });

            showMessage("Order created successfully");
            refreshOrders();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshOrders();
}

async function loadCustomerDropdown(selectId) {
    const select = document.getElementById(selectId);
    const customers = await apiGet("/customers/");

    customers.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.innerText = `${item.id} - ${item.name} (${item.phone})`;
        select.appendChild(option);
    });
}

async function loadVariantDropdown(selectId) {
    const select = document.getElementById(selectId);
    const variants = await apiGet("/variants/");

    variants.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.innerText = `${item.id} - ${item.sku} | Stock: ${item.stock_quantity} | Price: ${item.sell_price}`;
        select.appendChild(option);
    });
}

async function refreshOrders() {
    try {
        const data = await apiGet("/orders/");
        document.getElementById("orderTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("orderTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadPaymentsPage() {
    closeMobileMenu();
    setPage("Payments", "Create payments and track payment status.");

    setContent(`
        <div class="content-box">
            <h2>Create Payment</h2>
            <div id="messageBox" class="message"></div>

            <form id="paymentForm" class="form-grid">
                <select id="paymentOrder" required><option value="">Select order</option></select>
                <select id="paymentMethod" required>
                    <option value="">Payment method</option>
                    <option value="cash">Cash</option>
                    <option value="bkash">bKash</option>
                    <option value="nagad">Nagad</option>
                    <option value="card">Card</option>
                </select>
                <input id="paymentAmount" type="number" placeholder="Amount" required>
                <select id="paymentStatus" required>
                    <option value="paid">Paid</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                    <option value="refunded">Refunded</option>
                </select>
                <input id="transactionId" type="text" placeholder="Transaction ID">
                <button type="submit">Create Payment</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Payment List</h2>
            <div id="paymentTable">Loading...</div>
        </div>
    `);

    await loadOrderDropdown("paymentOrder");

    document.getElementById("paymentForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/payments/", {
                order_id: Number(document.getElementById("paymentOrder").value),
                payment_method: document.getElementById("paymentMethod").value,
                amount: Number(document.getElementById("paymentAmount").value),
                status: document.getElementById("paymentStatus").value,
                transaction_id: document.getElementById("transactionId").value || null
            });

            showMessage("Payment created successfully");
            refreshPayments();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshPayments();
}

async function loadOrderDropdown(selectId) {
    const select = document.getElementById(selectId);
    const orders = await apiGet("/orders/");

    orders.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.innerText = `${item.id} - ${item.order_number} | Final: ${item.final_amount} | Status: ${item.status}`;
        select.appendChild(option);
    });
}

async function refreshPayments() {
    try {
        const data = await apiGet("/payments/");
        document.getElementById("paymentTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("paymentTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadInvoicesPage() {
    closeMobileMenu();
    setPage("Invoices", "Generate, view, print and download invoices.");

    setContent(`
        <div class="content-box">
            <h2>Generate Invoice</h2>
            <div id="messageBox" class="message"></div>

            <form id="invoiceForm" class="form-grid">
                <select id="invoiceOrder" required><option value="">Select order</option></select>
                <button type="submit">Generate Invoice</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Invoice Preview</h2>
            <div class="invoice-actions">
                <button class="small-btn" onclick="printInvoice()">Print / Save PDF</button>
                <button class="small-btn" onclick="downloadInvoiceHtml()">Download HTML</button>
            </div>
            <div id="invoiceDetails">Select an order and generate invoice.</div>
        </div>

        <div class="content-box">
            <h2>Invoice List</h2>
            <div id="invoiceTable">Loading...</div>
        </div>
    `);

    await loadOrderDropdown("invoiceOrder");

    document.getElementById("invoiceForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            const orderId = document.getElementById("invoiceOrder").value;
            const invoice = await apiGet(`/orders/${orderId}/invoice`);
            currentInvoiceData = invoice;

            showMessage("Invoice generated successfully");
            document.getElementById("invoiceDetails").innerHTML = renderInvoice(invoice);
            refreshInvoices();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshInvoices();
}

async function refreshInvoices() {
    try {
        const data = await apiGet("/invoices/");
        document.getElementById("invoiceTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("invoiceTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

function renderInvoice(invoice) {
    let items = "";

    invoice.items.forEach((item, index) => {
        items += `<tr>
            <td>${index + 1}</td>
            <td>${item.product_name}</td>
            <td>${item.size}</td>
            <td>${item.color}</td>
            <td>${item.sku}</td>
            <td>${item.quantity}</td>
            <td>${money(item.unit_price)}</td>
            <td>${money(item.total_price)}</td>
        </tr>`;
    });

    return `
        <div id="printableInvoice" class="invoice-print-area">
            <div class="invoice-header">
                <div>
                    <h1>Fashion Store</h1>
                    <p>Rangpur, Bangladesh</p>
                    <p>Phone: 017000-0000</p>
                </div>

                <div class="invoice-meta">
                    <h2>INVOICE</h2>
                    <p><strong>Invoice:</strong> ${invoice.invoice_number}</p>
                    <p><strong>Order:</strong> ${invoice.order_number}</p>
                    <p><strong>Status:</strong> ${getBadge(invoice.payment_status)}</p>
                </div>
            </div>

            <div class="invoice-info-grid">
                <div class="invoice-info-box">
                    <h3>Bill To</h3>
                    <p>${invoice.customer_name}</p>
                    <p>${invoice.customer_phone}</p>
                </div>

                <div class="invoice-info-box">
                    <h3>Order Info</h3>
                    <p>Order Status: ${invoice.order_status}</p>
                    <p>Payment Status: ${invoice.payment_status}</p>
                </div>
            </div>

            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr><th>#</th><th>Product</th><th>Size</th><th>Color</th><th>SKU</th><th>Qty</th><th>Unit</th><th>Total</th></tr>
                    </thead>
                    <tbody>${items}</tbody>
                </table>
            </div>

            <div class="invoice-total-box">
                <div><span>Total:</span><strong>${money(invoice.total_amount)}</strong></div>
                <div><span>Discount:</span><strong>${money(invoice.discount)}</strong></div>
                <div><span>Final:</span><strong>${money(invoice.final_amount)}</strong></div>
                <div><span>Paid:</span><strong>${money(invoice.paid_amount)}</strong></div>
                <div><span>Due:</span><strong>${money(invoice.due_amount)}</strong></div>
            </div>
        </div>
    `;
}

function printInvoice() {
    if (!currentInvoiceData) {
        alert("Generate or view invoice first.");
        return;
    }

    window.print();
}

function downloadInvoiceHtml() {
    if (!currentInvoiceData) {
        alert("Generate or view invoice first.");
        return;
    }

    const html = document.getElementById("printableInvoice").outerHTML;
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `${currentInvoiceData.invoice_number}.html`;
    link.click();

    URL.revokeObjectURL(url);
}

function loadReportsPage() {
    closeMobileMenu();
    setPage("Reports", "View sales, profit and stock reports.");

    setContent(`
        <div class="cards">
            <div class="card" onclick="runReport('/reports/daily-sales', 'Daily Sales')"><h3>Daily Sales</h3><p>Today sales report.</p></div>
            <div class="card" onclick="runReport('/reports/monthly-sales', 'Monthly Sales')"><h3>Monthly Sales</h3><p>Monthly business summary.</p></div>
            <div class="card" onclick="runReport('/reports/top-products', 'Top Products')"><h3>Top Products</h3><p>Best-selling products.</p></div>
            <div class="card" onclick="runReport('/reports/profit', 'Profit')"><h3>Profit</h3><p>Sales, cost and profit.</p></div>
            <div class="card" onclick="runReport('/reports/low-stock', 'Low Stock')"><h3>Low Stock</h3><p>Low-stock products.</p></div>
        </div>

        <div class="content-box">
            <h2 id="reportTitle">Report Output</h2>
            <div id="reportOutput">Select a report.</div>
        </div>
    `);
}

async function runReport(url, title) {
    try {
        document.getElementById("reportTitle").innerText = title;

        if (url.includes("daily-sales")) {
            const today = new Date().toISOString().split("T")[0];
            url = `${url}?report_date=${today}`;
        }

        if (url.includes("monthly-sales")) {
            const now = new Date();
            url = `${url}?year=${now.getFullYear()}&month=${now.getMonth() + 1}`;
        }

        const data = await apiGet(url);
        document.getElementById("reportOutput").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("reportOutput").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadUsersPage() {
    closeMobileMenu();
    setPage("User Management", "Create admin/staff users, edit users and deactivate accounts.");

    setContent(`
        <div class="content-box">
            <h2>Create User</h2>
            <div id="messageBox" class="message"></div>

            <form id="userForm" class="form-grid">
                <input id="userFullName" type="text" placeholder="Full name" required>
                <input id="userEmail" type="email" placeholder="Email" required>
                <input id="userPhone" type="text" placeholder="Phone">
                <input id="userPassword" type="password" placeholder="Password" required>
                <select id="userRole" required>
                    <option value="">Select role</option>
                    <option value="admin">Admin</option>
                    <option value="staff">Staff</option>
                </select>
                <button type="submit">Create User</button>
            </form>
        </div>

        <div class="content-box">
            <h2>User List</h2>
            <div id="userTable">Loading...</div>
        </div>
    `);

    document.getElementById("userForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/users/", {
                full_name: document.getElementById("userFullName").value,
                email: document.getElementById("userEmail").value,
                phone: document.getElementById("userPhone").value || null,
                password: document.getElementById("userPassword").value,
                role: document.getElementById("userRole").value
            });

            showMessage("User created successfully");
            document.getElementById("userForm").reset();
            refreshUsers();
        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    refreshUsers();
}

async function refreshUsers() {
    try {
        userCache = await apiGet("/users/");

        let html = `<div class="table-wrapper"><table><thead><tr>
            <th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Role</th><th>Active</th><th>Actions</th>
        </tr></thead><tbody>`;

        userCache.forEach(item => {
            html += `<tr>
                <td>${item.id}</td>
                <td>${item.full_name}</td>
                <td>${item.email}</td>
                <td>${item.phone || ""}</td>
                <td>${getBadge(item.role)}</td>
                <td>${getBadge(item.is_active)}</td>
                <td>
                    <button class="small-btn" onclick="editUser(${item.id})">Edit</button>
                    <button class="small-btn danger" onclick="deleteUser(${item.id})">Deactivate</button>
                </td>
            </tr>`;
        });

        html += `</tbody></table></div>`;
        document.getElementById("userTable").innerHTML = html;
    } catch (error) {
        document.getElementById("userTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editUser(id) {
    const item = userCache.find(x => x.id === id);
    if (!item) return;

    const full_name = prompt("Full name:", item.full_name);
    const email = prompt("Email:", item.email);
    const phone = prompt("Phone:", item.phone || "");
    const role = prompt("Role admin/staff:", item.role);
    const is_active = prompt("Active true/false:", String(item.is_active));

    if (!full_name || !email || !role || !is_active) return;

    try {
        await apiPut(`/users/${id}`, {
            full_name,
            email,
            phone: phone || null,
            role,
            is_active: is_active.toLowerCase() === "true"
        });

        showMessage("User updated successfully");
        refreshUsers();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteUser(id) {
    if (!confirm("Deactivate this user?")) return;

    try {
        await apiDelete(`/users/${id}`);
        showMessage("User deactivated successfully");
        refreshUsers();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", async function() {
    await loadMe();
    loadDashboard();
});

/* Profile read-only view + edit mode upgrade */

function setProfileMode(mode) {
    const viewMode = document.getElementById("profileViewMode");
    const editMode = document.getElementById("profileEditMode");

    if (!viewMode || !editMode) return;

    if (mode === "edit") {
        viewMode.classList.add("hidden");
        editMode.classList.remove("hidden");
    } else {
        editMode.classList.add("hidden");
        viewMode.classList.remove("hidden");
    }
}

function openProfileEdit() {
    setProfileMode("edit");
}

function cancelProfileEdit() {
    if (currentUser) {
        fillProfile(currentUser);
    }

    setProfileMode("view");
}

function fillProfile(user) {
    const displayName = document.getElementById("profileDisplayName");
    const displayRole = document.getElementById("profileDisplayRole");

    const viewName = document.getElementById("profileViewName");
    const viewEmail = document.getElementById("profileViewEmail");
    const viewPhone = document.getElementById("profileViewPhone");

    const profileName = document.getElementById("profileName");
    const profileEmail = document.getElementById("profileEmail");
    const profilePhone = document.getElementById("profilePhone");

    if (displayName) displayName.innerText = user.full_name || "Account";
    if (displayRole) displayRole.innerText = `${user.role}`;

    if (viewName) viewName.innerText = user.full_name || "-";
    if (viewEmail) viewEmail.innerText = user.email || "-";
    if (viewPhone) viewPhone.innerText = user.phone || "Not added";

    if (profileName) profileName.value = user.full_name || "";
    if (profileEmail) profileEmail.value = user.email || "";
    if (profilePhone) profilePhone.value = user.phone || "";

    document.querySelectorAll(".profile-avatar").forEach(item => {
        item.innerText = user.email ? user.email[0].toUpperCase() : "A";
    });
}

function toggleProfilePanel() {
    document.getElementById("mobileMenu").classList.remove("open");

    const panel = document.getElementById("profilePanel");

    if (panel) {
        panel.classList.toggle("open");

        if (panel.classList.contains("open")) {
            setProfileMode("view");
        }
    }
}

async function loadMe() {
    if (!getToken()) {
        window.location.href = "/site/login.html";
        return;
    }

    try {
        const user = await apiGet("/auth/me");

        currentUser = user;
        document.body.dataset.role = user.role;

        localStorage.setItem("user_email", user.email);
        localStorage.setItem("user_role", user.role);

        fillProfile(user);
        setProfileMode("view");

    } catch (error) {
        logout();
    }
}

async function saveProfile() {
    try {
        const data = await apiPut("/auth/profile", {
            full_name: document.getElementById("profileName").value,
            phone: document.getElementById("profilePhone").value || null
        });

        setToken(data.access_token);

        currentUser = data.user;
        fillProfile(data.user);
        setProfileMode("view");

        showProfileMessage("Profile updated successfully");

    } catch (error) {
        showProfileMessage(error.message, "error");
    }
}

/* Final profile view/edit fix */

function setProfileMode(mode) {
    const viewMode = document.getElementById("profileViewMode");
    const editMode = document.getElementById("profileEditMode");

    if (!viewMode || !editMode) return;

    if (mode === "edit") {
        viewMode.classList.add("hidden");
        editMode.classList.remove("hidden");
    } else {
        editMode.classList.add("hidden");
        viewMode.classList.remove("hidden");
    }
}

function fillProfile(user) {
    const displayName = document.getElementById("profileDisplayName");
    const displayRole = document.getElementById("profileDisplayRole");

    const viewName = document.getElementById("profileViewName");
    const viewEmail = document.getElementById("profileViewEmail");
    const viewPhone = document.getElementById("profileViewPhone");

    const profileName = document.getElementById("profileName");
    const profileEmail = document.getElementById("profileEmail");
    const profilePhone = document.getElementById("profilePhone");

    if (displayName) displayName.innerText = user.full_name || "Account";
    if (displayRole) displayRole.innerText = user.role || "";

    if (viewName) viewName.innerText = user.full_name || "-";
    if (viewEmail) viewEmail.innerText = user.email || "-";
    if (viewPhone) viewPhone.innerText = user.phone || "Not added";

    if (profileName) profileName.value = user.full_name || "";
    if (profileEmail) profileEmail.value = user.email || "";
    if (profilePhone) profilePhone.value = user.phone || "";

    document.querySelectorAll(".profile-avatar").forEach(item => {
        item.innerText = user.email ? user.email[0].toUpperCase() : "A";
    });
}

function toggleProfilePanel() {
    const mobileMenu = document.getElementById("mobileMenu");
    const panel = document.getElementById("profilePanel");

    if (mobileMenu) {
        mobileMenu.classList.remove("open");
    }

    if (panel) {
        panel.classList.toggle("open");

        if (panel.classList.contains("open")) {
            setProfileMode("view");
            if (currentUser) fillProfile(currentUser);
        }
    }
}

function openProfileEdit() {
    setProfileMode("edit");
}

function cancelProfileEdit() {
    if (currentUser) fillProfile(currentUser);
    setProfileMode("view");
}

async function loadMe() {
    if (!getToken()) {
        window.location.href = "/site/login.html";
        return;
    }

    try {
        const user = await apiGet("/auth/me");

        currentUser = user;
        document.body.dataset.role = user.role;

        localStorage.setItem("user_email", user.email);
        localStorage.setItem("user_role", user.role);

        fillProfile(user);
        setProfileMode("view");

    } catch (error) {
        logout();
    }
}

async function saveProfile() {
    try {
        const data = await apiPut("/auth/profile", {
            full_name: document.getElementById("profileName").value,
            phone: document.getElementById("profilePhone").value || null
        });

        setToken(data.access_token);

        currentUser = data.user;
        fillProfile(data.user);
        setProfileMode("view");

        showProfileMessage("Profile updated successfully");

    } catch (error) {
        showProfileMessage(error.message, "error");
    }
}









/* AI Business Assistant */

function escapeHtml(text) {
    return String(text ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function prettifyKey(key) {
    return String(key)
        .replaceAll("_", " ")
        .replace(/\b\w/g, char => char.toUpperCase());
}

function getAiTime() {
    const now = new Date();
    return now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function renderAiData(data) {
    if (!data) return "";

    if (data.type === "metrics") {
        let html = `<div class="ai-result-box">`;

        if (data.title) {
            html += `<div class="ai-result-title">${escapeHtml(data.title)}</div>`;
        }

        html += `<div class="ai-metrics-grid">`;

        Object.entries(data.metrics || {}).forEach(([key, value]) => {
            html += `
                <div class="ai-metric-card">
                    <span>${escapeHtml(prettifyKey(key))}</span>
                    <strong>${escapeHtml(value)}</strong>
                </div>
            `;
        });

        html += `</div></div>`;
        return html;
    }

    if (data.type === "table") {
        const columns = data.columns || [];
        const rows = data.rows || [];
        const totals = data.totals || {};

        let html = `<div class="ai-result-box">`;

        if (data.title) {
            html += `<div class="ai-result-title">${escapeHtml(data.title)}</div>`;
        }

        if (Object.keys(totals).length > 0) {
            html += `<div class="ai-metrics-grid ai-small-metrics">`;

            Object.entries(totals).forEach(([key, value]) => {
                html += `
                    <div class="ai-metric-card">
                        <span>${escapeHtml(prettifyKey(key))}</span>
                        <strong>${escapeHtml(value)}</strong>
                    </div>
                `;
            });

            html += `</div>`;
        }

        if (rows.length === 0) {
            html += `<p class="ai-empty">No matching data found.</p></div>`;
            return html;
        }

        html += `<div class="ai-table-wrapper"><table class="ai-smart-table"><thead><tr>`;

        columns.forEach(column => {
            html += `<th>${escapeHtml(prettifyKey(column))}</th>`;
        });

        html += `</tr></thead><tbody>`;

        rows.forEach(row => {
            html += `<tr>`;

            columns.forEach(column => {
                html += `<td>${escapeHtml(row[column] ?? "")}</td>`;
            });

            html += `</tr>`;
        });

        html += `</tbody></table></div></div>`;
        return html;
    }

    if (typeof data === "object") {
        return `<pre class="ai-json">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
    }

    return "";
}

function loadAiAssistantPage() {
    closeMobileMenu();

    setPage("AI Assistant", "Ask business questions using your store database and free local Ollama AI.");

    setContent(`
        <div class="ai-page">

            <div class="ai-main-card">
                <div id="aiChatMessages" class="ai-chat-messages">
                    <div class="ai-message ai-message-bot">
                        <div class="ai-avatar bot">AI</div>

                        <div class="ai-bubble">
                            <div class="ai-message-top">
                                <strong>AI Assistant</strong>
                                <small>${getAiTime()}</small>
                            </div>

                            <p>
                                Hello! Ask me anything about your store data.
                                Example: <b>paid customers name and phone</b>,
                                <b>today sales</b>, <b>total profit</b>,
                                <b>due customers</b>, or <b>which products need restock?</b>
                            </p>
                        </div>
                    </div>
                </div>

                <form id="aiChatForm" class="ai-chat-form">
                    <input id="aiQuestion" type="text" placeholder="Ask anything about your store data..." required>

                    <button id="aiAskButton" type="submit">
                        Ask
                    </button>
                </form>
            </div>

            <aside class="ai-side-panel">
                <div class="ai-side-card">
                    <div class="ai-side-header">
                        <h3>Quick Questions</h3>
                        <button onclick="clearAiChat()">Clear Chat</button>
                    </div>

                    <div class="ai-question-group">
                        <h4>Business Summary</h4>
                        <button onclick="askAiSuggestion('business summary')">Overall shop summary</button>
                        <button onclick="askAiSuggestion('how is my shop doing today?')">How is my shop doing?</button>
                    </div>

                    <div class="ai-question-group">
                        <h4>Customers & Payments</h4>
                        <button onclick="askAiSuggestion('who bought products and paid?')">Who bought and paid?</button>
                        <button onclick="askAiSuggestion('paid customers name and phone')">Paid customers name & phone</button>
                        <button onclick="askAiSuggestion('who still needs to pay?')">Who still needs to pay?</button>
                        <button onclick="askAiSuggestion('show recent payments')">Recent payments</button>
                    </div>

                    <div class="ai-question-group">
                        <h4>Sales & Profit</h4>
                        <button onclick="askAiSuggestion('today sales')">Today sales</button>
                        <button onclick="askAiSuggestion('total profit')">Total profit</button>
                        <button onclick="askAiSuggestion('top selling products')">Top selling products</button>
                    </div>

                    <div class="ai-question-group">
                        <h4>Stock & Products</h4>
                        <button onclick="askAiSuggestion('which products need restock?')">Products need restock</button>
                        <button onclick="askAiSuggestion('total stock value')">Total stock value</button>
                        <button onclick="askAiSuggestion('show recent products')">Recent products</button>
                    </div>
                </div>
            </aside>

        </div>
    `);

    document.getElementById("aiChatForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const input = document.getElementById("aiQuestion");
        const question = input.value.trim();

        if (!question) return;

        input.value = "";
        await sendAiQuestion(question);
    });
}

function clearAiChat() {
    const container = document.getElementById("aiChatMessages");

    if (!container) return;

    container.innerHTML = `
        <div class="ai-message ai-message-bot">
            <div class="ai-avatar bot">AI</div>

            <div class="ai-bubble">
                <div class="ai-message-top">
                    <strong>AI Assistant</strong>
                    <small>${getAiTime()}</small>
                </div>

                <p>Chat cleared. Ask me anything about your store data.</p>
            </div>
        </div>
    `;
}

function addAiMessage(type, text, data = null, temporary = false) {
    const container = document.getElementById("aiChatMessages");

    if (!container) return null;

    const isUser = type === "user";
    const label = isUser ? "You" : "AI Assistant";
    const className = isUser ? "ai-message-user" : "ai-message-bot";
    const avatarText = isUser ? "YOU" : "AI";
    const avatarClass = isUser ? "user" : "bot";

    const message = document.createElement("div");
    message.className = `ai-message ${className}`;

    if (temporary) {
        message.classList.add("ai-temp-message");
    }

    let messageText = escapeHtml(text);

    if (temporary) {
        messageText = `
            <span class="ai-loader"></span>
            ${messageText}
        `;
    }

    message.innerHTML = `
        <div class="ai-avatar ${avatarClass}">${avatarText}</div>

        <div class="ai-bubble">
            <div class="ai-message-top">
                <strong>${label}</strong>
                <small>${getAiTime()}</small>
            </div>

            <p>${messageText}</p>
            ${renderAiData(data)}
        </div>
    `;

    container.appendChild(message);
    container.scrollTop = container.scrollHeight;

    return message;
}

async function sendAiQuestion(question) {
    const askButton = document.getElementById("aiAskButton");

    addAiMessage("user", question);

    if (askButton) {
        askButton.disabled = true;
        askButton.innerText = "Thinking...";
    }

    const thinkingMessage = addAiMessage("bot", "Checking your store data...", null, true);

    try {
        const response = await apiPost("/ai/chat", {
            question: question
        });

        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        addAiMessage("bot", response.answer, response.data);

    } catch (error) {
        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        addAiMessage("bot", error.message);
    } finally {
        if (askButton) {
            askButton.disabled = false;
            askButton.innerText = "Ask";
        }
    }
}

async function askAiSuggestion(question) {
    await sendAiQuestion(question);
}

/* Final Auth Token Expiry Handler */

function handleExpiredSession() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_role");

    alert("Your session expired. Please login again.");
    window.location.href = "/site/login.html";
}

async function apiRequest(url, options = {}) {
    const token = getToken();

    if (!token) {
        handleExpiredSession();
        throw new Error("No login token found");
    }

    const headers = {
        ...(options.headers || {}),
        "Authorization": `Bearer ${token}`
    };

    if (options.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url, {
        ...options,
        headers: headers
    });

    let data = null;

    try {
        data = await response.json();
    } catch {}

    if (response.status === 401) {
        handleExpiredSession();
        throw new Error("Invalid or expired token");
    }

    if (response.status === 403) {
        throw new Error(formatApiError(data) || "Access forbidden");
    }

    if (!response.ok) {
        throw new Error(formatApiError(data));
    }

    return data;
}

async function apiGet(url) {
    return apiRequest(url);
}

async function apiPost(url, body) {
    return apiRequest(url, {
        method: "POST",
        body: JSON.stringify(body)
    });
}

async function apiPut(url, body) {
    return apiRequest(url, {
        method: "PUT",
        body: JSON.stringify(body)
    });
}

async function apiDelete(url) {
    return apiRequest(url, {
        method: "DELETE"
    });
}
