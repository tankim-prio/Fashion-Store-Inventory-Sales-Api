function getToken() {
    return localStorage.getItem("access_token");
}

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_role");
    window.location.href = "/site/login.html";
}

function setPage(title, subtitle) {
    document.getElementById("pageTitle").innerText = title;
    document.getElementById("pageSubtitle").innerText = subtitle;
}

function setContent(html) {
    document.getElementById("mainContent").innerHTML = html;
}

async function apiGet(url) {
    const response = await fetch(url, {
        headers: {
            "Authorization": `Bearer ${getToken()}`
        }
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Request failed");
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

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Request failed");
    }

    return data;
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

function showMessage(message, type = "success") {
    const box = document.getElementById("messageBox");
    if (!box) return;

    box.className = type === "success" ? "message success" : "message error";
    box.innerText = message;
    box.style.display = "block";
}

async function loadMe() {
    if (!getToken()) {
        window.location.href = "/site/login.html";
        return;
    }

    try {
        const user = await apiGet("/auth/me");
        document.getElementById("accountInfo").innerText = `${user.email} (${user.role})`;

        const icon = document.querySelector(".account-icon");
        icon.innerText = user.email[0].toUpperCase();
    } catch (error) {
        logout();
    }
}

function loadDashboard() {
    setPage("Dashboard V2", "Interactive dashboard is working.");

    setContent(`
        <div class="cards">
            <div class="card" onclick="loadCategoriesPage()">
                <h3>Categories</h3>
                <p>Create and view categories.</p>
            </div>

            <div class="card" onclick="loadProductsPage()">
                <h3>Products</h3>
                <p>Create and search products.</p>
            </div>

            <div class="card" onclick="loadVariantsPage()">
                <h3>Variants</h3>
                <p>Create product variants.</p>
            </div>

            <div class="card" onclick="loadQuick('/reports/profit', 'Reports')">
                <h3>Reports</h3>
                <p>View reports.</p>
            </div>
        </div>
    `);
}

async function loadCategoriesPage() {
    setPage("Categories", "Create and view categories.");

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
                description: document.getElementById("categoryDescription").value
            });

            showMessage("Category created successfully");
            document.getElementById("categoryName").value = "";
            document.getElementById("categoryDescription").value = "";
            await refreshCategories();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshCategories();
}

async function refreshCategories() {
    try {
        const data = await apiGet("/categories/");
        document.getElementById("categoryTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("categoryTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadProductsPage() {
    setPage("Products", "Create, view and search products.");

    setContent(`
        <div class="content-box">
            <h2>Create Product</h2>
            <div id="messageBox" class="message"></div>

            <form id="productForm" class="form-grid">
                <input id="productName" type="text" placeholder="Product name" required>

                <select id="productCategory" required>
                    <option value="">Select category</option>
                </select>

                <input id="productBrand" type="text" placeholder="Brand">
                <input id="productDescription" type="text" placeholder="Description">

                <button type="submit">Create Product</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Search Products</h2>
            <div class="form-grid">
                <input id="productSearch" type="text" placeholder="Search product name">
                <button onclick="searchProducts()">Search</button>
                <button onclick="refreshProducts()">Show All</button>
            </div>
        </div>

        <div class="content-box">
            <h2>Product List</h2>
            <div id="productTable">Loading...</div>
        </div>
    `);

    await loadCategoryDropdown();

    document.getElementById("productForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/products/", {
                name: document.getElementById("productName").value,
                category_id: Number(document.getElementById("productCategory").value),
                brand: document.getElementById("productBrand").value,
                description: document.getElementById("productDescription").value
            });

            showMessage("Product created successfully");
            await refreshProducts();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshProducts();
}

async function loadCategoryDropdown() {
    const select = document.getElementById("productCategory");
    const categories = await apiGet("/categories/");

    categories.forEach(category => {
        const option = document.createElement("option");
        option.value = category.id;
        option.innerText = `${category.id} - ${category.name}`;
        select.appendChild(option);
    });
}

async function refreshProducts() {
    try {
        const data = await apiGet("/products/");
        document.getElementById("productTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("productTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function searchProducts() {
    const search = document.getElementById("productSearch").value;

    try {
        const data = await apiGet(`/products/?search=${encodeURIComponent(search)}`);
        document.getElementById("productTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("productTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadVariantsPage() {
    setPage("Variants", "Create and view product variants.");

    setContent(`
        <div class="content-box">
            <h2>Create Variant</h2>
            <div id="messageBox" class="message"></div>

            <form id="variantForm" class="form-grid">
                <select id="variantProduct" required>
                    <option value="">Select product</option>
                </select>

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

    await loadProductDropdown();

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
            await refreshVariants();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshVariants();
}

async function loadProductDropdown() {
    const select = document.getElementById("variantProduct");
    const products = await apiGet("/products/");

    products.forEach(product => {
        const option = document.createElement("option");
        option.value = product.id;
        option.innerText = `${product.id} - ${product.name}`;
        select.appendChild(option);
    });
}

async function refreshVariants() {
    try {
        const data = await apiGet("/variants/");
        document.getElementById("variantTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("variantTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadQuick(url, title) {
    setPage(title, `Quick view for ${title}.`);

    setContent(`
        <div class="content-box">
            <h2>${title}</h2>
            <div id="quickTable">Loading...</div>
        </div>
    `);

    try {
        const data = await apiGet(url);
        document.getElementById("quickTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("quickTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    loadMe();
});

async function loadCustomersPage() {
    setPage("Customers", "Create, view and search customers.");

    setContent(`
        <div class="content-box">
            <h2>Create Customer</h2>
            <div id="messageBox" class="message"></div>

            <form id="customerForm" class="form-grid">
                <input id="customerName" type="text" placeholder="Customer name" required>
                <input id="customerPhone" type="text" placeholder="Phone number" required>
                <input id="customerEmail" type="email" placeholder="Email">
                <input id="customerAddress" type="text" placeholder="Address">
                <button type="submit">Create Customer</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Search Customers</h2>
            <div class="form-grid">
                <input id="customerSearch" type="text" placeholder="Search by name, phone, email">
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

            document.getElementById("customerName").value = "";
            document.getElementById("customerPhone").value = "";
            document.getElementById("customerEmail").value = "";
            document.getElementById("customerAddress").value = "";

            await refreshCustomers();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshCustomers();
}

async function refreshCustomers() {
    try {
        const data = await apiGet("/customers/");
        document.getElementById("customerTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("customerTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function searchCustomers() {
    const search = document.getElementById("customerSearch").value;

    try {
        const data = await apiGet(`/customers/?search=${encodeURIComponent(search)}`);
        document.getElementById("customerTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("customerTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadOrdersPage() {
    setPage("Orders", "Create orders from customer and product variants.");

    setContent(`
        <div class="content-box">
            <h2>Create Order</h2>
            <div id="messageBox" class="message"></div>

            <form id="orderForm" class="form-grid">
                <select id="orderCustomer" required>
                    <option value="">Select customer</option>
                </select>

                <select id="orderVariant" required>
                    <option value="">Select variant</option>
                </select>

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

    await loadCustomerDropdown();
    await loadVariantDropdown();

    document.getElementById("orderForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const createdBy = localStorage.getItem("user_email") || "Dashboard User";

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
                created_by: createdBy
            });

            showMessage("Order created successfully. Stock reduced automatically.");

            document.getElementById("orderQuantity").value = "";
            document.getElementById("orderDiscount").value = "0";

            await refreshOrders();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshOrders();
}

async function loadCustomerDropdown() {
    const select = document.getElementById("orderCustomer");
    const customers = await apiGet("/customers/");

    customers.forEach(customer => {
        const option = document.createElement("option");
        option.value = customer.id;
        option.innerText = `${customer.id} - ${customer.name} (${customer.phone})`;
        select.appendChild(option);
    });
}

async function loadVariantDropdown() {
    const select = document.getElementById("orderVariant");
    const variants = await apiGet("/variants/");

    variants.forEach(variant => {
        const option = document.createElement("option");
        option.value = variant.id;
        option.innerText = `${variant.id} - ${variant.sku} | ${variant.size} | ${variant.color} | Stock: ${variant.stock_quantity} | Price: ${variant.sell_price}`;
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
    setPage("Payments", "Receive payments for orders.");

    setContent(`
        <div class="content-box">
            <h2>Create Payment</h2>
            <div id="messageBox" class="message"></div>

            <form id="paymentForm" class="form-grid">
                <select id="paymentOrder" required>
                    <option value="">Select order</option>
                </select>

                <select id="paymentMethod" required>
                    <option value="">Select payment method</option>
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

                <input id="transactionId" type="text" placeholder="Transaction ID optional">

                <button type="submit">Create Payment</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Payment List</h2>
            <div id="paymentTable">Loading...</div>
        </div>
    `);

    await loadOrderDropdown();

    document.getElementById("paymentForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const transactionValue = document.getElementById("transactionId").value;

        try {
            await apiPost("/payments/", {
                order_id: Number(document.getElementById("paymentOrder").value),
                payment_method: document.getElementById("paymentMethod").value,
                amount: Number(document.getElementById("paymentAmount").value),
                status: document.getElementById("paymentStatus").value,
                transaction_id: transactionValue || null
            });

            showMessage("Payment created successfully. If fully paid, order status becomes paid.");

            document.getElementById("paymentAmount").value = "";
            document.getElementById("transactionId").value = "";

            await refreshPayments();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshPayments();
}

async function loadOrderDropdown() {
    const select = document.getElementById("paymentOrder");
    const orders = await apiGet("/orders/");

    orders.forEach(order => {
        const option = document.createElement("option");
        option.value = order.id;
        option.innerText = `${order.id} - ${order.order_number} | Final: ${order.final_amount} | Status: ${order.status}`;
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
    setPage("Invoices", "Generate invoice from order and view invoice details.");

    setContent(`
        <div class="content-box">
            <h2>Generate Invoice</h2>
            <div id="messageBox" class="message"></div>

            <form id="invoiceForm" class="form-grid">
                <select id="invoiceOrder" required>
                    <option value="">Select order</option>
                </select>

                <button type="submit">Generate Invoice</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Invoice Details</h2>
            <div id="invoiceDetails">Select an order and generate invoice.</div>
        </div>

        <div class="content-box">
            <h2>Invoice List</h2>
            <div id="invoiceTable">Loading...</div>
        </div>
    `);

    await loadInvoiceOrderDropdown();

    document.getElementById("invoiceForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const orderId = document.getElementById("invoiceOrder").value;

        try {
            const invoice = await apiGet(`/orders/${orderId}/invoice`);

            showMessage("Invoice generated successfully");
            document.getElementById("invoiceDetails").innerHTML = renderInvoice(invoice);

            await refreshInvoices();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshInvoices();
}

async function loadInvoiceOrderDropdown() {
    const select = document.getElementById("invoiceOrder");
    const orders = await apiGet("/orders/");

    orders.forEach(order => {
        const option = document.createElement("option");
        option.value = order.id;
        option.innerText = `${order.id} - ${order.order_number} | Final: ${order.final_amount} | Status: ${order.status}`;
        select.appendChild(option);
    });
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
    let itemsHtml = "";

    invoice.items.forEach(item => {
        itemsHtml += `
            <tr>
                <td>${item.product_name}</td>
                <td>${item.size}</td>
                <td>${item.color}</td>
                <td>${item.sku}</td>
                <td>${item.quantity}</td>
                <td>${item.unit_price}</td>
                <td>${item.total_price}</td>
            </tr>
        `;
    });

    return `
        <div class="invoice-box">
            <h2>Invoice: ${invoice.invoice_number}</h2>

            <p><strong>Order:</strong> ${invoice.order_number}</p>
            <p><strong>Order Status:</strong> ${invoice.order_status}</p>

            <p><strong>Customer:</strong> ${invoice.customer_name}</p>
            <p><strong>Phone:</strong> ${invoice.customer_phone}</p>

            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Size</th>
                        <th>Color</th>
                        <th>SKU</th>
                        <th>Qty</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${itemsHtml}
                </tbody>
            </table>

            <div class="invoice-summary">
                <p><strong>Total Amount:</strong> ${invoice.total_amount}</p>
                <p><strong>Discount:</strong> ${invoice.discount}</p>
                <p><strong>Final Amount:</strong> ${invoice.final_amount}</p>
                <p><strong>Paid Amount:</strong> ${invoice.paid_amount}</p>
                <p><strong>Due Amount:</strong> ${invoice.due_amount}</p>
                <p><strong>Payment Status:</strong> ${invoice.payment_status}</p>
            </div>
        </div>
    `;
}

async function loadReportsPage() {
    setPage("Reports", "View sales, profit, top products and low-stock reports.");

    setContent(`
        <div class="cards">
            <div class="card" onclick="loadDailySalesReport()">
                <h3>Daily Sales</h3>
                <p>View today's or selected date sales.</p>
            </div>

            <div class="card" onclick="loadMonthlySalesReport()">
                <h3>Monthly Sales</h3>
                <p>View monthly business summary.</p>
            </div>

            <div class="card" onclick="loadTopProductsReport()">
                <h3>Top Products</h3>
                <p>View best-selling products.</p>
            </div>

            <div class="card" onclick="loadProfitReport()">
                <h3>Profit</h3>
                <p>View total sales, cost and profit.</p>
            </div>

            <div class="card" onclick="loadLowStockReport()">
                <h3>Low Stock</h3>
                <p>View products with low stock.</p>
            </div>
        </div>

        <div class="content-box">
            <h2>Report Output</h2>
            <div id="reportOutput">Select a report.</div>
        </div>
    `);
}

async function loadDailySalesReport() {
    const today = new Date().toISOString().split("T")[0];

    document.getElementById("reportOutput").innerHTML = `
        <div class="form-grid">
            <input id="dailyReportDate" type="date" value="${today}">
            <button onclick="runDailySalesReport()">Run Daily Report</button>
        </div>

        <div id="dailyReportResult">Choose date and run report.</div>
    `;
}

async function runDailySalesReport() {
    const reportDate = document.getElementById("dailyReportDate").value;

    try {
        const data = await apiGet(`/reports/daily-sales?report_date=${reportDate}`);
        document.getElementById("dailyReportResult").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("dailyReportResult").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadMonthlySalesReport() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    document.getElementById("reportOutput").innerHTML = `
        <div class="form-grid">
            <input id="monthlyReportYear" type="number" value="${year}" placeholder="Year">
            <input id="monthlyReportMonth" type="number" value="${month}" placeholder="Month">
            <button onclick="runMonthlySalesReport()">Run Monthly Report</button>
        </div>

        <div id="monthlyReportResult">Choose year/month and run report.</div>
    `;
}

async function runMonthlySalesReport() {
    const year = document.getElementById("monthlyReportYear").value;
    const month = document.getElementById("monthlyReportMonth").value;

    try {
        const data = await apiGet(`/reports/monthly-sales?year=${year}&month=${month}`);
        document.getElementById("monthlyReportResult").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("monthlyReportResult").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadTopProductsReport() {
    document.getElementById("reportOutput").innerHTML = `
        <div class="form-grid">
            <input id="topProductLimit" type="number" value="5" placeholder="Limit">
            <button onclick="runTopProductsReport()">Run Top Products Report</button>
        </div>

        <div id="topProductsResult">Choose limit and run report.</div>
    `;
}

async function runTopProductsReport() {
    const limit = document.getElementById("topProductLimit").value;

    try {
        const data = await apiGet(`/reports/top-products?limit=${limit}`);
        document.getElementById("topProductsResult").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("topProductsResult").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadProfitReport() {
    try {
        const data = await apiGet("/reports/profit");
        document.getElementById("reportOutput").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("reportOutput").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadLowStockReport() {
    document.getElementById("reportOutput").innerHTML = `
        <div class="form-grid">
            <input id="lowStockThreshold" type="number" value="5" placeholder="Threshold">
            <button onclick="runLowStockReport()">Run Low Stock Report</button>
        </div>

        <div id="lowStockResult">Choose threshold and run report.</div>
    `;
}

async function runLowStockReport() {
    const threshold = document.getElementById("lowStockThreshold").value;

    try {
        const data = await apiGet(`/reports/low-stock?threshold=${threshold}`);
        document.getElementById("lowStockResult").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("lowStockResult").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
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

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Update failed");
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

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Delete failed");
    }

    return data;
}

function renderCategoryTable(categories) {
    if (!categories.length) {
        return "<p>No category found.</p>";
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    categories.forEach(category => {
        html += `
            <tr>
                <td>${category.id}</td>
                <td>${category.name}</td>
                <td>${category.description || ""}</td>
                <td>
                    <button class="small-btn" onclick="editCategory(${category.id}, '${category.name}', '${category.description || ""}')">Edit</button>
                    <button class="small-btn danger" onclick="deleteCategory(${category.id})">Delete</button>
                </td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    return html;
}

async function refreshCategories() {
    try {
        const data = await apiGet("/categories/");
        document.getElementById("categoryTable").innerHTML = renderCategoryTable(data);
    } catch (error) {
        document.getElementById("categoryTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editCategory(id, oldName, oldDescription) {
    const name = prompt("Enter new category name:", oldName);
    if (!name) return;

    const description = prompt("Enter new description:", oldDescription);

    try {
        await apiPut(`/categories/${id}`, {
            name,
            description
        });

        showMessage("Category updated successfully");
        await refreshCategories();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteCategory(id) {
    const confirmDelete = confirm("Delete this category? Only delete if no product uses this category.");
    if (!confirmDelete) return;

    try {
        await apiDelete(`/categories/${id}`);
        showMessage("Category deleted successfully");
        await refreshCategories();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderProductTable(products) {
    if (!products.length) {
        return "<p>No product found.</p>";
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Category ID</th>
                    <th>Brand</th>
                    <th>Description</th>
                    <th>Active</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    products.forEach(product => {
        html += `
            <tr>
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>${product.category_id}</td>
                <td>${product.brand || ""}</td>
                <td>${product.description || ""}</td>
                <td>${product.is_active}</td>
                <td>
                    <button class="small-btn" onclick="editProduct(${product.id}, '${product.name}', ${product.category_id}, '${product.brand || ""}', '${product.description || ""}')">Edit</button>
                    <button class="small-btn danger" onclick="deleteProduct(${product.id})">Delete</button>
                </td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    return html;
}

async function refreshProducts() {
    try {
        const data = await apiGet("/products/");
        document.getElementById("productTable").innerHTML = renderProductTable(data);
    } catch (error) {
        document.getElementById("productTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function searchProducts() {
    const search = document.getElementById("productSearch").value;

    try {
        const data = await apiGet(`/products/?search=${encodeURIComponent(search)}`);
        document.getElementById("productTable").innerHTML = renderProductTable(data);
    } catch (error) {
        document.getElementById("productTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editProduct(id, oldName, oldCategoryId, oldBrand, oldDescription) {
    const name = prompt("Enter product name:", oldName);
    if (!name) return;

    const categoryId = prompt("Enter category ID:", oldCategoryId);
    if (!categoryId) return;

    const brand = prompt("Enter brand:", oldBrand);
    const description = prompt("Enter description:", oldDescription);

    try {
        await apiPut(`/products/${id}`, {
            name,
            category_id: Number(categoryId),
            brand,
            description
        });

        showMessage("Product updated successfully");
        await refreshProducts();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteProduct(id) {
    const confirmDelete = confirm("Delete this product?");
    if (!confirmDelete) return;

    try {
        await apiDelete(`/products/${id}`);
        showMessage("Product deleted successfully");
        await refreshProducts();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderVariantTable(variants) {
    if (!variants.length) {
        return "<p>No variant found.</p>";
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Product ID</th>
                    <th>Size</th>
                    <th>Color</th>
                    <th>Buy Price</th>
                    <th>Sell Price</th>
                    <th>Stock</th>
                    <th>SKU</th>
                    <th>Active</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    variants.forEach(variant => {
        html += `
            <tr>
                <td>${variant.id}</td>
                <td>${variant.product_id}</td>
                <td>${variant.size}</td>
                <td>${variant.color}</td>
                <td>${variant.buy_price}</td>
                <td>${variant.sell_price}</td>
                <td>${variant.stock_quantity}</td>
                <td>${variant.sku}</td>
                <td>${variant.is_active}</td>
                <td>
                    <button class="small-btn" onclick="editVariant(${variant.id}, ${variant.product_id}, '${variant.size}', '${variant.color}', ${variant.buy_price}, ${variant.sell_price}, ${variant.stock_quantity}, '${variant.sku}')">Edit</button>
                    <button class="small-btn danger" onclick="deleteVariant(${variant.id})">Delete</button>
                </td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    return html;
}

async function refreshVariants() {
    try {
        const data = await apiGet("/variants/");
        document.getElementById("variantTable").innerHTML = renderVariantTable(data);
    } catch (error) {
        document.getElementById("variantTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editVariant(id, oldProductId, oldSize, oldColor, oldBuyPrice, oldSellPrice, oldStock, oldSku) {
    const productId = prompt("Enter product ID:", oldProductId);
    if (!productId) return;

    const size = prompt("Enter size:", oldSize);
    if (!size) return;

    const color = prompt("Enter color:", oldColor);
    if (!color) return;

    const buyPrice = prompt("Enter buy price:", oldBuyPrice);
    if (!buyPrice) return;

    const sellPrice = prompt("Enter sell price:", oldSellPrice);
    if (!sellPrice) return;

    const stock = prompt("Enter stock quantity:", oldStock);
    if (!stock) return;

    const sku = prompt("Enter SKU:", oldSku);
    if (!sku) return;

    try {
        await apiPut(`/variants/${id}`, {
            product_id: Number(productId),
            size,
            color,
            buy_price: Number(buyPrice),
            sell_price: Number(sellPrice),
            stock_quantity: Number(stock),
            sku
        });

        showMessage("Variant updated successfully");
        await refreshVariants();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteVariant(id) {
    const confirmDelete = confirm("Delete this variant?");
    if (!confirmDelete) return;

    try {
        await apiDelete(`/variants/${id}`);
        showMessage("Variant deleted successfully");
        await refreshVariants();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderCustomerTable(customers) {
    if (!customers.length) {
        return "<p>No customer found.</p>";
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Email</th>
                    <th>Address</th>
                    <th>Active</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    customers.forEach(customer => {
        html += `
            <tr>
                <td>${customer.id}</td>
                <td>${customer.name}</td>
                <td>${customer.phone}</td>
                <td>${customer.email || ""}</td>
                <td>${customer.address || ""}</td>
                <td>${customer.is_active}</td>
                <td>
                    <button class="small-btn" onclick="editCustomer(${customer.id}, '${customer.name}', '${customer.phone}', '${customer.email || ""}', '${customer.address || ""}')">Edit</button>
                    <button class="small-btn danger" onclick="deleteCustomer(${customer.id})">Delete</button>
                </td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    return html;
}

async function refreshCustomers() {
    try {
        const data = await apiGet("/customers/");
        document.getElementById("customerTable").innerHTML = renderCustomerTable(data);
    } catch (error) {
        document.getElementById("customerTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function searchCustomers() {
    const search = document.getElementById("customerSearch").value;

    try {
        const data = await apiGet(`/customers/?search=${encodeURIComponent(search)}`);
        document.getElementById("customerTable").innerHTML = renderCustomerTable(data);
    } catch (error) {
        document.getElementById("customerTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editCustomer(id, oldName, oldPhone, oldEmail, oldAddress) {
    const name = prompt("Enter customer name:", oldName);
    if (!name) return;

    const phone = prompt("Enter phone:", oldPhone);
    if (!phone) return;

    const email = prompt("Enter email:", oldEmail);
    const address = prompt("Enter address:", oldAddress);

    try {
        await apiPut(`/customers/${id}`, {
            name,
            phone,
            email: email || null,
            address: address || null
        });

        showMessage("Customer updated successfully");
        await refreshCustomers();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteCustomer(id) {
    const confirmDelete = confirm("Delete this customer?");
    if (!confirmDelete) return;

    try {
        await apiDelete(`/customers/${id}`);
        showMessage("Customer deleted successfully");
        await refreshCustomers();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function loadStockPage() {
    setPage("Stock Management", "Add stock, remove stock, view stock history and check low-stock products.");

    setContent(`
        <div class="content-box">
            <h2>Current Variant Stock</h2>
            <button class="small-btn" onclick="refreshVariantStockTable()">Refresh Stock</button>
            <div id="variantStockTable">Loading...</div>
        </div>

        <div class="content-box">
            <h2>Add Stock</h2>
            <div id="messageBox" class="message"></div>

            <form id="addStockForm" class="form-grid">
                <select id="addStockVariant" required>
                    <option value="">Select variant</option>
                </select>

                <input id="addStockQuantity" type="number" placeholder="Quantity to add" required>
                <input id="addStockNote" type="text" placeholder="Note optional">

                <button type="submit">Add Stock</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Remove Stock</h2>

            <form id="removeStockForm" class="form-grid">
                <select id="removeStockVariant" required>
                    <option value="">Select variant</option>
                </select>

                <input id="removeStockQuantity" type="number" placeholder="Quantity to remove" required>
                <input id="removeStockNote" type="text" placeholder="Note optional">

                <button type="submit">Remove Stock</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Stock History</h2>

            <div class="form-grid">
                <select id="historyVariant">
                    <option value="">All variants</option>
                </select>

                <button onclick="refreshStockHistory()">Load History</button>
            </div>

            <div id="stockHistoryTable">Loading...</div>
        </div>

        <div class="content-box">
            <h2>Low Stock</h2>

            <div class="form-grid">
                <input id="lowStockLimit" type="number" value="5" placeholder="Low stock limit">
                <button onclick="refreshLowStockFromStockPage()">Check Low Stock</button>
            </div>

            <div id="lowStockTable">Choose limit and check low stock.</div>
        </div>
    `);

    await loadStockVariantDropdowns();

    document.getElementById("addStockForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const createdBy = localStorage.getItem("user_email") || "Dashboard User";

        try {
            await apiPost("/stock/add", {
                variant_id: Number(document.getElementById("addStockVariant").value),
                quantity: Number(document.getElementById("addStockQuantity").value),
                note: document.getElementById("addStockNote").value || null,
                created_by: createdBy
            });

            showMessage("Stock added successfully");

            document.getElementById("addStockQuantity").value = "";
            document.getElementById("addStockNote").value = "";

            await refreshVariantStockTable();
            await refreshStockHistory();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    document.getElementById("removeStockForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const createdBy = localStorage.getItem("user_email") || "Dashboard User";

        try {
            await apiPost("/stock/remove", {
                variant_id: Number(document.getElementById("removeStockVariant").value),
                quantity: Number(document.getElementById("removeStockQuantity").value),
                note: document.getElementById("removeStockNote").value || null,
                created_by: createdBy
            });

            showMessage("Stock removed successfully");

            document.getElementById("removeStockQuantity").value = "";
            document.getElementById("removeStockNote").value = "";

            await refreshVariantStockTable();
            await refreshStockHistory();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshVariantStockTable();
    await refreshStockHistory();
}

async function loadStockVariantDropdowns() {
    const addSelect = document.getElementById("addStockVariant");
    const removeSelect = document.getElementById("removeStockVariant");
    const historySelect = document.getElementById("historyVariant");

    try {
        const variants = await apiGet("/variants/");

        variants.forEach(variant => {
            const label = `${variant.id} - ${variant.sku} | ${variant.size} | ${variant.color} | Stock: ${variant.stock_quantity}`;

            const addOption = document.createElement("option");
            addOption.value = variant.id;
            addOption.innerText = label;
            addSelect.appendChild(addOption);

            const removeOption = document.createElement("option");
            removeOption.value = variant.id;
            removeOption.innerText = label;
            removeSelect.appendChild(removeOption);

            const historyOption = document.createElement("option");
            historyOption.value = variant.id;
            historyOption.innerText = label;
            historySelect.appendChild(historyOption);
        });

    } catch (error) {
        showMessage("Could not load variants. Create product variants first.", "error");
    }
}

function renderVariantStockTable(variants) {
    if (!variants.length) {
        return "<p>No variants found.</p>";
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Product ID</th>
                    <th>SKU</th>
                    <th>Size</th>
                    <th>Color</th>
                    <th>Sell Price</th>
                    <th>Current Stock</th>
                    <th>Active</th>
                </tr>
            </thead>
            <tbody>
    `;

    variants.forEach(variant => {
        html += `
            <tr>
                <td>${variant.id}</td>
                <td>${variant.product_id}</td>
                <td>${variant.sku}</td>
                <td>${variant.size}</td>
                <td>${variant.color}</td>
                <td>${variant.sell_price}</td>
                <td><strong>${variant.stock_quantity}</strong></td>
                <td>${variant.is_active}</td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    return html;
}

async function refreshVariantStockTable() {
    try {
        const variants = await apiGet("/variants/");
        document.getElementById("variantStockTable").innerHTML = renderVariantStockTable(variants);
    } catch (error) {
        document.getElementById("variantStockTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function refreshStockHistory() {
    const variantId = document.getElementById("historyVariant") ? document.getElementById("historyVariant").value : "";

    let url = "/stock/history";

    if (variantId) {
        url = `/stock/history?variant_id=${variantId}`;
    }

    try {
        const history = await apiGet(url);
        document.getElementById("stockHistoryTable").innerHTML = renderTable(history);
    } catch (error) {
        document.getElementById("stockHistoryTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function refreshLowStockFromStockPage() {
    const limit = document.getElementById("lowStockLimit").value || 5;

    try {
        const data = await apiGet(`/stock/low?threshold=${limit}`);
        document.getElementById("lowStockTable").innerHTML = renderTable(data);
    } catch (error) {
        document.getElementById("lowStockTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

let userCache = [];

async function loadUsersPage() {
    setPage("User Management", "Create admin/staff users, edit users and deactivate accounts.");

    setContent(`
        <div class="content-box">
            <h2>Create User</h2>
            <div id="messageBox" class="message"></div>

            <form id="userForm" class="form-grid">
                <input id="userFullName" type="text" placeholder="Full name" required>
                <input id="userEmail" type="email" placeholder="Email" required>
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
            <button class="small-btn" onclick="refreshUsers()">Refresh Users</button>
            <div id="userTable">Loading...</div>
        </div>
    `);

    document.getElementById("userForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            await apiPost("/users/", {
                full_name: document.getElementById("userFullName").value,
                email: document.getElementById("userEmail").value,
                password: document.getElementById("userPassword").value,
                role: document.getElementById("userRole").value
            });

            showMessage("User created successfully");

            document.getElementById("userFullName").value = "";
            document.getElementById("userEmail").value = "";
            document.getElementById("userPassword").value = "";
            document.getElementById("userRole").value = "";

            await refreshUsers();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshUsers();
}

function renderUserTable(users) {
    userCache = users;

    if (!users.length) {
        return "<p>No user found.</p>";
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Full Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Active</th>
                    <th>Created At</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    users.forEach(user => {
        html += `
            <tr>
                <td>${user.id}</td>
                <td>${user.full_name}</td>
                <td>${user.email}</td>
                <td><strong>${user.role}</strong></td>
                <td>${user.is_active}</td>
                <td>${user.created_at || ""}</td>
                <td>
                    <button class="small-btn" onclick="editUser(${user.id})">Edit</button>
                    <button class="small-btn danger" onclick="deleteUser(${user.id})">Deactivate</button>
                </td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    return html;
}

async function refreshUsers() {
    try {
        const data = await apiGet("/users/");
        document.getElementById("userTable").innerHTML = renderUserTable(data);
    } catch (error) {
        document.getElementById("userTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function editUser(id) {
    const user = userCache.find(item => item.id === id);

    if (!user) {
        showMessage("User not found in table", "error");
        return;
    }

    const fullName = prompt("Enter full name:", user.full_name);
    if (!fullName) return;

    const email = prompt("Enter email:", user.email);
    if (!email) return;

    const role = prompt("Enter role: admin or staff", user.role);
    if (!role) return;

    if (!["admin", "staff"].includes(role)) {
        showMessage("Role must be admin or staff", "error");
        return;
    }

    const activeInput = prompt("Is user active? true or false", String(user.is_active));
    if (!activeInput) return;

    const isActive = activeInput.toLowerCase() === "true";

    try {
        await apiPut(`/users/${id}`, {
            full_name: fullName,
            email: email,
            role: role,
            is_active: isActive
        });

        showMessage("User updated successfully");
        await refreshUsers();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deleteUser(id) {
    const confirmDelete = confirm("Deactivate this user? The user will not be able to login.");
    if (!confirmDelete) return;

    try {
        await apiDelete(`/users/${id}`);
        showMessage("User deactivated successfully");
        await refreshUsers();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

function getBadge(value) {
    if (value === true) {
        return `<span class="badge badge-active">active</span>`;
    }

    if (value === false) {
        return `<span class="badge badge-inactive">inactive</span>`;
    }

    if (value === null || value === undefined) {
        return "";
    }

    const text = String(value).toLowerCase();

    if (["paid", "active", "admin"].includes(text)) {
        return `<span class="badge badge-paid">${value}</span>`;
    }

    if (["pending", "staff"].includes(text)) {
        return `<span class="badge badge-pending">${value}</span>`;
    }

    if (["failed", "cancelled", "refunded", "inactive"].includes(text)) {
        return `<span class="badge badge-failed">${value}</span>`;
    }

    return value;
}

function formatCell(key, value) {
    if (value === null || value === undefined) {
        return "";
    }

    if (key.includes("status") || key === "role" || key === "is_active") {
        return getBadge(value);
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return value;
}

function renderTable(data) {
    if (!Array.isArray(data)) {
        data = [data];
    }

    if (data.length === 0) {
        return "<p>No data found.</p>";
    }

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

function safeNumber(value) {
    const numberValue = Number(value);
    return Number.isNaN(numberValue) ? 0 : numberValue;
}

function money(value) {
    return safeNumber(value).toFixed(2);
}

async function loadDashboard() {
    setPage("Dashboard", "Business overview, stock health, sales summary and recent activity.");

    setContent(`
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Products</h3>
                <div class="stat-number" id="statProducts">...</div>
                <div class="stat-note">Active product catalog</div>
            </div>

            <div class="stat-card">
                <h3>Total Stock</h3>
                <div class="stat-number" id="statStock">...</div>
                <div class="stat-note">All variant quantity</div>
            </div>

            <div class="stat-card">
                <h3>Total Orders</h3>
                <div class="stat-number" id="statOrders">...</div>
                <div class="stat-note">All customer orders</div>
            </div>

            <div class="stat-card">
                <h3>Total Profit</h3>
                <div class="stat-number" id="statProfit">...</div>
                <div class="stat-note">Based on profit report</div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Categories</h3>
                <div class="stat-number" id="statCategories">...</div>
                <div class="stat-note">Product groups</div>
            </div>

            <div class="stat-card">
                <h3>Customers</h3>
                <div class="stat-number" id="statCustomers">...</div>
                <div class="stat-note">Saved customers</div>
            </div>

            <div class="stat-card">
                <h3>Paid Orders</h3>
                <div class="stat-number" id="statPaidOrders">...</div>
                <div class="stat-note">Completed sales</div>
            </div>

            <div class="stat-card">
                <h3>Low Stock</h3>
                <div class="stat-number" id="statLowStock">...</div>
                <div class="stat-note">Stock less than or equal 5</div>
            </div>
        </div>

        <div class="dashboard-row">
            <div class="content-box">
                <div class="action-title">
                    <h2>Recent Orders</h2>
                    <button class="small-btn" onclick="loadOrdersPage()">View Orders</button>
                </div>
                <div id="recentOrdersTable">Loading...</div>
            </div>

            <div class="content-box">
                <div class="action-title">
                    <h2>Low Stock Preview</h2>
                    <button class="small-btn" onclick="loadStockPage()">Manage Stock</button>
                </div>
                <div id="dashboardLowStockTable">Loading...</div>
            </div>
        </div>
    `);

    await refreshDashboardStats();
}

async function refreshDashboardStats() {
    try {
        const categories = await apiGet("/categories/");
        const products = await apiGet("/products/");
        const variants = await apiGet("/variants/");
        const customers = await apiGet("/customers/");
        const orders = await apiGet("/orders/");
        const profit = await apiGet("/reports/profit");

        const totalStock = variants.reduce((sum, item) => sum + safeNumber(item.stock_quantity), 0);
        const lowStockItems = variants.filter(item => safeNumber(item.stock_quantity) <= 5);
        const paidOrders = orders.filter(order => String(order.status).toLowerCase() === "paid");

        document.getElementById("statProducts").innerText = products.length;
        document.getElementById("statStock").innerText = totalStock;
        document.getElementById("statOrders").innerText = orders.length;
        document.getElementById("statProfit").innerText = money(profit.total_profit || profit.profit || 0);

        document.getElementById("statCategories").innerText = categories.length;
        document.getElementById("statCustomers").innerText = customers.length;
        document.getElementById("statPaidOrders").innerText = paidOrders.length;
        document.getElementById("statLowStock").innerText = lowStockItems.length;

        const recentOrders = orders.slice(-5).reverse();
        document.getElementById("recentOrdersTable").innerHTML = renderTable(recentOrders);

        const lowStockPreview = lowStockItems.slice(0, 5);
        document.getElementById("dashboardLowStockTable").innerHTML = renderTable(lowStockPreview);

    } catch (error) {
        setContent(`<div class="content-box"><p class="error-text">${error.message}</p></div>`);
    }
}

async function loadOrdersPage() {
    setPage("Orders", "Create orders, filter by customer/status and view order list.");

    setContent(`
        <div class="content-box">
            <h2>Create Order</h2>
            <div id="messageBox" class="message"></div>

            <form id="orderForm" class="form-grid">
                <select id="orderCustomer" required>
                    <option value="">Select customer</option>
                </select>

                <select id="orderVariant" required>
                    <option value="">Select variant</option>
                </select>

                <input id="orderQuantity" type="number" placeholder="Quantity" required>
                <input id="orderDiscount" type="number" placeholder="Discount" value="0">

                <button type="submit">Create Order</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Order Filters</h2>

            <div class="filter-box">
                <div class="form-grid">
                    <select id="filterOrderCustomer">
                        <option value="">All customers</option>
                    </select>

                    <select id="filterOrderStatus">
                        <option value="">All statuses</option>
                        <option value="pending">Pending</option>
                        <option value="paid">Paid</option>
                        <option value="cancelled">Cancelled</option>
                        <option value="refunded">Refunded</option>
                    </select>

                    <button onclick="refreshOrders()">Apply Filter</button>
                </div>
            </div>

            <div id="orderTable">Loading...</div>
        </div>
    `);

    await loadCustomerDropdown();
    await loadVariantDropdown();
    await loadOrderFilterCustomerDropdown();

    document.getElementById("orderForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const createdBy = localStorage.getItem("user_email") || "Dashboard User";

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
                created_by: createdBy
            });

            showMessage("Order created successfully. Stock reduced automatically.");

            document.getElementById("orderQuantity").value = "";
            document.getElementById("orderDiscount").value = "0";

            await refreshOrders();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshOrders();
}

async function loadOrderFilterCustomerDropdown() {
    const select = document.getElementById("filterOrderCustomer");
    const customers = await apiGet("/customers/");

    customers.forEach(customer => {
        const option = document.createElement("option");
        option.value = customer.id;
        option.innerText = `${customer.id} - ${customer.name}`;
        select.appendChild(option);
    });
}

async function refreshOrders() {
    try {
        const customerId = document.getElementById("filterOrderCustomer") ? document.getElementById("filterOrderCustomer").value : "";
        const status = document.getElementById("filterOrderStatus") ? document.getElementById("filterOrderStatus").value : "";

        const params = new URLSearchParams();

        if (customerId) params.append("customer_id", customerId);
        if (status) params.append("status", status);

        const url = params.toString() ? `/orders/?${params.toString()}` : "/orders/";
        const data = await apiGet(url);

        document.getElementById("orderTable").innerHTML = renderTable(data);

    } catch (error) {
        document.getElementById("orderTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}

async function loadPaymentsPage() {
    setPage("Payments", "Create payments, filter payments and track payment status.");

    setContent(`
        <div class="content-box">
            <h2>Create Payment</h2>
            <div id="messageBox" class="message"></div>

            <form id="paymentForm" class="form-grid">
                <select id="paymentOrder" required>
                    <option value="">Select order</option>
                </select>

                <select id="paymentMethod" required>
                    <option value="">Select payment method</option>
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

                <input id="transactionId" type="text" placeholder="Transaction ID optional">

                <button type="submit">Create Payment</button>
            </form>
        </div>

        <div class="content-box">
            <h2>Payment Filters</h2>

            <div class="filter-box">
                <div class="form-grid">
                    <input id="filterPaymentOrderId" type="number" placeholder="Order ID">

                    <select id="filterPaymentStatus">
                        <option value="">All statuses</option>
                        <option value="paid">Paid</option>
                        <option value="pending">Pending</option>
                        <option value="failed">Failed</option>
                        <option value="refunded">Refunded</option>
                    </select>

                    <select id="filterPaymentMethod">
                        <option value="">All methods</option>
                        <option value="cash">Cash</option>
                        <option value="bkash">bKash</option>
                        <option value="nagad">Nagad</option>
                        <option value="card">Card</option>
                    </select>

                    <button onclick="refreshPayments()">Apply Filter</button>
                </div>
            </div>

            <div id="paymentTable">Loading...</div>
        </div>
    `);

    await loadOrderDropdown();

    document.getElementById("paymentForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        const transactionValue = document.getElementById("transactionId").value;

        try {
            await apiPost("/payments/", {
                order_id: Number(document.getElementById("paymentOrder").value),
                payment_method: document.getElementById("paymentMethod").value,
                amount: Number(document.getElementById("paymentAmount").value),
                status: document.getElementById("paymentStatus").value,
                transaction_id: transactionValue || null
            });

            showMessage("Payment created successfully.");

            document.getElementById("paymentAmount").value = "";
            document.getElementById("transactionId").value = "";

            await refreshPayments();

        } catch (error) {
            showMessage(error.message, "error");
        }
    });

    await refreshPayments();
}

async function refreshPayments() {
    try {
        const orderId = document.getElementById("filterPaymentOrderId") ? document.getElementById("filterPaymentOrderId").value : "";
        const status = document.getElementById("filterPaymentStatus") ? document.getElementById("filterPaymentStatus").value : "";
        const method = document.getElementById("filterPaymentMethod") ? document.getElementById("filterPaymentMethod").value : "";

        const params = new URLSearchParams();

        if (orderId) params.append("order_id", orderId);
        if (status) params.append("status", status);
        if (method) params.append("payment_method", method);

        const url = params.toString() ? `/payments/?${params.toString()}` : "/payments/";
        const data = await apiGet(url);

        document.getElementById("paymentTable").innerHTML = renderTable(data);

    } catch (error) {
        document.getElementById("paymentTable").innerHTML = `<p class="error-text">${error.message}</p>`;
    }
}
