# 🪙 Expense Management API

A comprehensive and robust RESTful API for tracking and managing personal expenses. Built with FastAPI, this application provides features for user authentication, expense and category management, detailed reporting, and data exporting capabilities.

## 📜 Table of Contents
- [Key Features](#key-Features)
- [Technology Stack](#Technology-Stack)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Setup / Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [License](#license)

---

## ✨ Key Features
- **User Authentication:** Secure registration and login using JWT tokens with password hashing via bcrypt.
- **Expense Tracking:** Full CRUD functionality for expenses.
- **Category Management:** Organize expenses with customizable categories (name, color, icon). Deleting a category gracefully handles associated expenses.
- **Insightful Reports:**
  - Monthly Reports: Summary of spending and number of transactions.
  - Yearly Reports: Detailed annual breakdown with top spending categories.
- **Data Export:** Export user expense data (CSV, Excel, JSON) with flexible filters.
- **API Security:** IP-based rate limiting, rigorous input validation using Pydantic.
- **High Performance:** FastAPI + Starlette with async support and GZip compression.
- **Interactive Documentation:** Swagger UI (/docs) and ReDoc (/redoc).

---

## 🛠️ Technology Stack
- Backend: Python 3.9+
- Framework: FastAPI
- Database: SQLAlchemy ORM with PostgreSQL
- Data Validation: Pydantic
- Authentication: python-jose (JWT), passlib[bcrypt]
- Testing: Pytest with in-memory SQLite database
- Server: Uvicorn

---

## 📁 Project Structure
```
/
├── .env                  # Environment variables file
├── main.py               # FastAPI app entrypoint, middleware
├── config.py             # Configuration management using Pydantic
├── database.py           # SQLAlchemy database setup
├── models.py             # ORM models (User, Expense, Category)
├── schemas.py            # Pydantic schemas
├── crud.py               # Database logic (CRUD)
├── auth.py               # Authentication logic
├── routers/              # API route handlers
│   ├── users.py
│   ├── expenses.py
│   ├── categories.py
│   ├── reports.py
│   └── export.py
└── tests/                # Test suite
    └── conftest.py       # Pytest fixtures
```

---

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /login` - Authenticate and receive JWT token

### Expenses
- `POST /expenses/` - Create expense
- `GET /expenses/` - List expenses (paginated)
- `GET /expenses/{expense_id}` - Retrieve expense
- `PUT /expenses/{expense_id}` - Update expense
- `DELETE /expenses/{expense_id}` - Delete expense

### Categories
- `POST /categories/` - Create category
- `GET /categories/` - List categories
- `GET /categories/{category_id}` - Retrieve category
- `PUT /categories/{category_id}` - Update category
- `DELETE /categories/{category_id}` - Delete category

### Reports
- `GET /reports/monthly/{year}/{month}` - Monthly report
- `GET /reports/yearly/{year}` - Yearly report

### Export
- `POST /export/` - Export expenses with filters (date range, categories, format)

---

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL database
- pip (package manager)

---

## Setup / Installation

### 1. Clone the repository:
```bash
git clone https://github.com/your-username/expense-management-api.git
cd expense-management-api
```

### 2. Create and activate a virtual environment:
```bash
# Unix/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```
*(Optional: `pip freeze > requirements.txt` to generate the file)*

---

## Environment Variables
Create a `.env` file in the root directory with:
```bash
DATABASE_URL="postgresql+psycopg2://postgres:password@localhost:5432/expenses_db"
SECRET_KEY="your_super_secret_key_change_this"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Running the Application
```bash
uvicorn main:app --reload
```
- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## ✅ Running Tests
```bash
pytest
```
Tests run on an in-memory SQLite database for isolation.

---

## 📄 License
MIT License. See [LICENSE](https://opensource.org/licenses/MIT) for details.
