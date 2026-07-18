[![Backend CI](https://github.com/tankim-prio/fashion-store-inventory-sales-api/actions/workflows/ci.yml/badge.svg)](https://github.com/tankim-prio/fashion-store-inventory-sales-api/actions/workflows/ci.yml)

﻿# Fashion Store Inventory & Sales Management API

A complete **FastAPI backend portfolio project** for managing fashion store inventory, sales, customers, orders, payments, invoices, reports, AI Assistant, and Predictive Analytics.

This project is designed as a production-style backend system for a fashion retail business. It demonstrates real-world backend development, database design, authentication, business workflow implementation, automated testing, AI integration, and analytics-based decision support.

---

## Project Overview

Fashion retail stores need a system to manage products, stock, customers, sales, payments, invoices, and business decisions. This project solves that problem with a complete backend API and frontend dashboard.

The system allows store admins and staff to:

- Manage products, categories, variants, and stock
- Track customers and order history
- Create orders and receive payments
- Generate invoices
- View sales and profit reports
- Ask business questions through an AI Assistant
- Use Predictive Analytics for forecasting, stock risk, restock planning, customer insights, and product recommendations

This is not only a CRUD project. It includes authentication, role-based access, business logic, AI Assistant, predictive analytics, frontend integration, demo data, documentation, and automated tests.

---
## Project Demonstration

Watch the complete demonstration of the **Fashion Store Inventory & Sales API**, featuring its FastAPI backend, inventory and sales workflows, AI Assistant, predictive analytics, authentication, reporting, and administrative dashboard.

[![Watch the Fashion Store API Project Demonstration](assets/project-demo-thumbnail.png)](https://youtu.be/KSIN9vOkGxg)

<p align="center">
  <a href="https://youtu.be/KSIN9vOkGxg">
    <strong>▶ Watch the Complete Project Demonstration on YouTube</strong>
  </a>
</p>

---

### Demonstration Highlights

- Dashboard and business overview
- AI-powered business assistant
- Predictive analytics and product recommendations
- Category, product and variant management
- Inventory tracking and stock history
- Customer, order and payment workflows
- Invoice generation and business reports
- Authentication, profiles and role-based user management

> **Source Code:** This repository contains the complete FastAPI application, setup instructions, API documentation, Docker configuration, and automated tests.

---
## Application Screenshots

A visual overview of the Fashion Store platform, covering its dashboard, AI-powered features, inventory operations, sales workflow, reporting, and user administration.

---

### 1. Dashboard, AI Assistant and Analytics

#### Dashboard

Business overview featuring product, stock, order, profit, and recent activity summaries.

![Fashion Store Dashboard](<assets/screenshots/01. Dashboard.jpeg>)

#### AI Assistant

An AI-powered assistant for answering questions about sales, customers, payments, products, and stock.

![AI Business Assistant](<assets/screenshots/02. AI Assistant.jpeg>)

#### Predictive Analytics

Business intelligence for sales forecasting, stock-risk prediction, restock planning, customer insights, and product recommendations.

![Predictive Analytics Dashboard](<assets/screenshots/03. Analytics.jpeg>)

---

### 2. Product and Inventory Management

#### Categories

Create, view, update, and manage product categories.

![Category Management](<assets/screenshots/04. Categories.jpeg>)

#### Products

Create, search, update, and manage fashion products.

![Product Management](<assets/screenshots/05. Products.jpeg>)

#### Product Variants

Manage product sizes, colours, prices, stock quantities, and SKUs.

![Product Variant Management](<assets/screenshots/06. Variants.jpeg>)

#### Stock Management

Monitor current stock, record stock movements, review stock history, and identify low-stock items.

![Stock Management](<assets/screenshots/07. Stock Management.jpeg>)

---

### 3. Customers, Orders and Payments

#### Customers

Create, search, update, and manage customer records.

![Customer Management](<assets/screenshots/08. Customers.jpeg>)

#### Orders

Create customer orders, apply discounts, and monitor order status.

![Order Management](<assets/screenshots/09. Orders.jpeg>)

#### Payments

Record payments using different methods and track pending or completed transactions.

![Payment Management](<assets/screenshots/10. Payments.jpeg>)

---

### 4. Invoices and Business Reports

#### Invoices

Generate, preview, print, and download customer invoices.

![Invoice Generation and Preview](<assets/screenshots/11. Invoices.jpeg>)

#### Reports

Review daily and monthly sales, top products, profit, and low-stock reports.

![Sales and Inventory Reports](<assets/screenshots/12. Reports.jpeg>)

---

### 5. User Management and Authentication

#### User Management

Create and manage admin or staff accounts with role and account-status controls.

![Admin and Staff User Management](<assets/screenshots/13. User Management.jpeg>)

#### User Profile

View account information and access profile-management options.

![User Profile](<assets/screenshots/14. Profile Icon.jpeg>)

#### Edit Profile

Update the authenticated user’s name and phone information.

![Profile Editing](<assets/screenshots/15. Profile (Edit).jpeg>)

#### Login

Secure login interface for registered admin and staff accounts.

![Authentication Login](<assets/screenshots/16. Login.jpeg>)

---

## Key Features

### Authentication and Authorization

- JWT-based login system
- Admin and staff role management
- Protected API routes
- Account profile update
- Token expiry handling
- Secure password hashing

### Category Management

- Create categories
- View category list
- Update categories
- Delete or deactivate categories
- Duplicate category protection

### Product Management

- Create products
- View product list
- Update product details
- Product-category relationship
- Product validation

### Product Variant Management

- Size and color management
- SKU-based variant tracking
- Buy price and sell price
- Stock quantity per variant
- Sell price validation
- Duplicate SKU protection

### Stock Management

- Add stock
- Remove stock
- Track stock movement
- View low-stock products
- Prevent invalid stock operations

### Customer Management

- Create customers
- View customers
- Update customer information
- Validate phone and email
- Support customer-based order tracking

### Order Management

- Create customer orders
- Add multiple products to an order
- Automatic stock reduction after order creation
- Order status handling
- Pending, paid, cancelled, and refunded order support
- Due amount calculation

### Payment Management

- Create payments for orders
- Support partial payment
- Prevent overpayment
- Payment method tracking
- Automatic order payment status update

### Invoice Management

- Generate invoice data from orders
- Printable invoice page
- Customer, order, item, payment, and due summary

### Reports

- Daily sales report
- Monthly sales report
- Profit summary
- Top-selling products
- Low-stock report

---

## AI Assistant

The project includes a local AI-powered business assistant using **Ollama**.

The AI Assistant can answer business questions from the database and analytics engine.

Example questions:

```text
Who bought products and paid?
Who still needs to pay?
Show today sales
How much profit did we make?
Which products should I restock?
Forecast next 7 days sales
Show customer insights
Recommend products for customer 1
```

### AI Assistant Capabilities

- Natural language business question handling
- Rule-based intent detection for fast answers
- Local LLM support using Ollama
- Database-grounded responses
- Business summary generation
- Customer payment insights
- Stock and sales analysis
- Predictive analytics integration

### AI Assistant Design

The AI system uses a hybrid approach:

```text
User Question
     ↓
Intent Detection
     ↓
Safe Business Logic / SQLAlchemy Query
     ↓
Analytics Engine if needed
     ↓
Structured Response for Dashboard
```

The AI Assistant is designed to avoid unsafe direct SQL generation. It uses controlled backend logic and safe SQLAlchemy queries.

---

## Predictive Analytics and ML-Style Intelligence

This project includes a Predictive Analytics module for business decision support.

The analytics system helps the store owner understand future sales, stock risk, customer behavior, and product demand.

### Analytics Modules

| Module | Description |
|---|---|
| Analytics Overview | Summary of business intelligence metrics |
| Sales Forecast | Predicts upcoming sales using recent sales trends |
| Stock Risk Prediction | Finds products that may run out soon |
| Restock Plan | Suggests which products should be purchased again |
| Customer Insights | Segments customers based on purchase behavior |
| Product Recommendations | Recommends products using sales and customer history |

### Sales Forecast

The sales forecast module estimates future sales using recent order and payment patterns.

It helps answer:

```text
How much sales can we expect in the next 7 days?
What is the recent sales trend?
How is the business performing?
```

### Stock Risk Prediction

The stock risk module identifies products that may become low stock or out of stock.

It helps answer:

```text
Which products are risky?
Which products may run out soon?
Which items need attention?
```

### Restock Plan

The restock plan recommends which products should be purchased again.

It considers:

- Current stock
- Recent sales demand
- Lead time
- Safety stock
- Estimated buying requirement

### Customer Insights

The customer insights module analyzes customers based on:

- Total spending
- Purchase count
- Last purchase date
- Customer activity

It helps identify:

- VIP customers
- Regular customers
- New customers
- Inactive customers

### Product Recommendations

The recommendation module suggests products using:

- Product popularity
- Available stock
- Customer purchase history
- Category preference

It supports both:

- General product recommendations
- Customer-based product recommendations

---

## Technology Stack

| Area | Tools and Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Authentication | JWT |
| Password Security | bcrypt / passlib |
| API Documentation | Swagger UI |
| AI Assistant | Ollama local LLM |
| Analytics Logic | Python business analytics |
| Testing | Pytest, FastAPI TestClient |
| Frontend | HTML, CSS, JavaScript |
| Version Control | Git, GitHub |
| Environment Config | python-dotenv |
| Server | Uvicorn |

---

## Skills Demonstrated

### Backend Engineering Skills

- REST API development
- FastAPI project architecture
- PostgreSQL database modeling
- SQLAlchemy ORM relationships
- Pydantic schema validation
- JWT authentication
- Role-based access control
- Error handling
- Business logic implementation
- API documentation
- Test-driven backend validation

### Database Skills

- Relational database design
- One-to-many relationships
- Product-category relationship
- Product-variant relationship
- Order-order items relationship
- Customer-order relationship
- Payment-order relationship
- Query optimization basics
- Transaction-safe business operations

### AI and Analytics Skills

- Local LLM integration
- AI Assistant workflow design
- Intent detection
- Database-grounded AI responses
- Sales forecasting logic
- Stock risk analysis
- Customer segmentation
- Product recommendation logic
- Business intelligence dashboard support

### Software Engineering Skills

- Clean project structure
- Environment variable management
- Git and GitHub workflow
- Automated testing
- Professional documentation
- Demo seed data generation
- Portfolio-ready project presentation

---

## Project Structure

```text
fashion_store_api/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── stock.py
│   │
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── dependencies/
│   └── utils/
│
├── frontend/
│   ├── login.html
│   ├── dashboard_v2.html
│   └── assets/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_categories_products.py
│   ├── test_customers.py
│   ├── test_variants_stock.py
│   ├── test_predictive_analytics.py
│   └── test_ai_assistant_analytics.py
│
├── docs/
│   ├── API_OVERVIEW.md
│   ├── TESTING.md
│   ├── AI_AND_ANALYTICS.md
│   ├── PORTFOLIO_SUMMARY.md
│   ├── DEMO_GUIDE.md
│   └── SCREENSHOT_CHECKLIST.md
│
├── seed_demo_data.py
├── requirements.txt
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── PROJECT_STATUS.md
└── README.md
```

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tankim-prio/fashion-store-inventory-sales-api.git
cd fashion-store-inventory-sales-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create PostgreSQL Database

Create a database named:

```text
fashion_store_db
```

### 6. Configure Environment Variables

Create a `.env` file from `.env.example`.

Example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/fashion_store_db
SECRET_KEY=my_super_secret_key_123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

OLLAMA_MODEL=qwen2.5:3b
OLLAMA_URL=http://127.0.0.1:11434/api/generate
OLLAMA_TIMEOUT_SECONDS=25
OLLAMA_KEEP_ALIVE=30m
AI_OLLAMA_FIRST=true
```

### 7. Seed Demo Data

```bash
python seed_demo_data.py
```

### 8. Run the Server

```bash
uvicorn app.main:app --reload
```

---

## Important URLs

Swagger API Documentation:

```text
http://127.0.0.1:8000/docs
```

Frontend Login:

```text
http://127.0.0.1:8000/site/login.html
```

Dashboard:

```text
http://127.0.0.1:8000/site/dashboard_v2.html
```

---

## Demo Credentials

```text
Admin Email: admin.demo@gmail.com
Password: 123456

Staff Email: staff.demo@gmail.com
Password: 123456
```

---

## Ollama Setup for AI Assistant

Install Ollama and pull the recommended model:

```bash
ollama pull qwen2.5:3b
```

Run the model:

```bash
ollama run qwen2.5:3b
```

The AI Assistant can work locally without paid API usage.

---


---

## Docker Support

This project supports Docker-based local development.

Docker setup includes:

- FastAPI backend container
- PostgreSQL database container
- Docker Compose configuration
- Docker environment example file
- Docker guide documentation

Run with Docker:

```bash
docker compose up --build
```

Seed Docker database:

```bash
docker compose exec api python seed_demo_data.py
```

Run tests inside Docker:

```bash
docker compose exec api python -m pytest -v
```

Docker URLs:

```text
Swagger Docs: http://127.0.0.1:8000/docs
Login Page: http://127.0.0.1:8000/site/login.html
Dashboard: http://127.0.0.1:8000/site/dashboard_v2.html
```


## Automated Testing

Run all tests:

```bash
python -m pytest -v
```

Current test result:

```text
29 passed
```

Test coverage includes:

- Authentication
- Protected routes
- Categories
- Products
- Customers
- Product variants
- Stock management
- AI Assistant
- Predictive Analytics

---


---

## GitHub Actions CI/CD

This project includes a GitHub Actions workflow for automated quality checking.

The CI workflow runs on every push and pull request to the main branch.

It checks:

- Python dependency installation
- PostgreSQL service setup
- Demo data seeding
- Automated backend tests
- Docker image build

Current test result:

```text
29 passed
```


## API Modules

| Module | Endpoint Prefix |
|---|---|
| Authentication | `/auth` |
| Users | `/users` |
| Categories | `/categories` |
| Products | `/products` |
| Variants | `/variants` |
| Customers | `/customers` |
| Orders | `/orders` |
| Payments | `/payments` |
| Invoices | `/invoices` |
| Reports | `/reports` |
| AI Assistant | `/ai` |
| Predictive Analytics | `/ml` |

---

## Documentation

Additional documentation:

- [API Overview](docs/API_OVERVIEW.md)
- [Testing Guide](docs/TESTING.md)
- [AI and Analytics](docs/AI_AND_ANALYTICS.md)
- [Portfolio Summary](docs/PORTFOLIO_SUMMARY.md)
- [Demo Guide](docs/DEMO_GUIDE.md)
- [Screenshot Checklist](docs/SCREENSHOT_CHECKLIST.md)
- [Docker Guide](docs/DOCKER_GUIDE.md)

---

## Why This Project Is Strong for Portfolio

This project is stronger than a simple CRUD application because it includes:

- Real retail business workflow
- Authentication and authorization
- Relational database design
- Stock and order transaction logic
- Payment and invoice flow
- Reports and business summaries
- AI Assistant
- Predictive Analytics
- Frontend dashboard
- Automated tests
- Demo seed data
- Professional documentation

It demonstrates both **Python backend engineering** and **AI/analytics integration** in one complete project.

---

## Possible Future Improvements

- Docker support
- GitHub Actions CI/CD
- Cloud deployment
- Redis caching
- Background jobs
- PDF invoice export
- Excel report export
- Multi-outlet inventory support
- Advanced ML model training
- Admin dashboard charts

---

## Project Status

Current status:

```text
Completed and portfolio-ready
```

Test result:

```text
29 passed
```

---

## Author

Built as a professional backend and AI portfolio project.
