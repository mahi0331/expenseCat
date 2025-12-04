# Expense Tracker Application

A comprehensive Python-based expense tracking application with budget management, alerts, reporting, and group expense sharing (Splitwise-like) functionality.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [Option 1: Docker Setup (Recommended)](#option-1-docker-setup-recommended)
  - [Option 2: Local Setup](#option-2-local-setup)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Test Cases](#test-cases)
- [Database Schema](#database-schema)
- [Code Documentation](#code-documentation)
- [Features Implementation](#features-implementation)

---

## 🎯 Features

### Core Requirements ✅

- **Expense Logging**: Track daily expenses with categories, amounts, and descriptions
- **Expense Categories**: Pre-defined categories (Food, Transport, Entertainment, etc.) with ability to add custom ones
- **Monthly Budgets**: Set budgets for each category per month
- **Budget Alerts**: Automatic alerts when exceeding budget limits
- **Basic Reports**: 
  - Total spending per month
  - Spending vs budget comparison per category

### Extra Credit Features ⭐

- **Different Budgets for Different Months**: Set and manage unique budgets for each month and category combination
- **Custom Alerts**: Configure alert thresholds (e.g., alert when only 10% budget remaining)
- **Email Notifications**: Automated email alerts for budget warnings and exceeded budgets
- **Group Expense Sharing**: Splitwise-like functionality for sharing expenses among users with balance tracking

---

## 🛠 Technology Stack

- **Language**: Python 3.11
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Email**: SMTP (Gmail compatible)
- **Containerization**: Docker & Docker Compose
- **CLI Framework**: Custom implementation with colorama for colored output
- **Data Presentation**: Tabulate for formatted tables

---

## 📁 Project Structure

```
expense-tracker/
│
├── main.py                 # CLI entry point and user interface
├── models.py               # SQLAlchemy database models
├── database.py             # Database initialization and session management
├── services.py             # Business logic layer
├── email_service.py        # Email notification service
├── config.py               # Configuration management
├── utils.py                # Utility functions
│
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Multi-container Docker setup
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
│
└── README.md               # This file
```

---

## 🚀 Setup Instructions

### Option 1: Docker Setup (Recommended)

Docker provides an isolated, consistent environment and is the easiest way to run the application.

#### Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)

#### Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd expense-tracker
   ```

2. **Configure environment (optional for email)**
   ```bash
   cp .env.example .env
   # Edit .env file to add email credentials if you want email notifications
   ```

3. **Build and start containers**
   ```bash
   docker-compose up -d
   ```
   This will:
   - Build the Python application image
   - Start PostgreSQL database container
   - Start the application container

4. **Access the application**
   ```bash
   docker exec -it expense_tracker_app python main.py
   ```

5. **Stop the application**
   ```bash
   docker-compose down
   ```

6. **Stop and remove all data (including database)**
   ```bash
   docker-compose down -v
   ```

---

### Option 2: Local Setup

#### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- pip (Python package manager)

#### Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd expense-tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database**
   ```sql
   -- Connect to PostgreSQL and run:
   CREATE DATABASE expense_tracker;
   CREATE USER expense_user WITH PASSWORD 'expense_pass';
   GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials and email settings
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

---

## ⚙️ Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```env
# Database Configuration
DATABASE_URL=postgresql://expense_user:expense_pass@localhost:5432/expense_tracker

# Email Configuration (Optional - for email alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Alert Configuration
DEFAULT_ALERT_THRESHOLD=10
```

### Email Setup (Gmail Example)

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account Settings → Security → 2-Step Verification → App Passwords
   - Generate a new app password for "Mail"
3. Use the generated password in `SMTP_PASSWORD`

**Note**: Email notifications are optional. The application works without email configuration, but alerts will only appear in the terminal.

---

## 📖 Usage Guide

### Getting Started

1. **Start the application**
   ```bash
   # Docker
   docker exec -it expense_tracker_app python main.py

   # Local
   python main.py
   ```

2. **Register a new user**
   - Choose option `2` from login menu
   - Enter username and email
   - System will create default alert settings

3. **Main Menu Navigation**
   The application provides an interactive menu-driven interface:
   ```
   1. Add Expense
   2. View Expenses
   3. Manage Budgets
   4. View Reports
   5. Manage Alerts
   6. Group Expenses (Splitwise)
   7. Categories
   8. Logout
   9. Exit
   ```

### Common Workflows

#### Adding an Expense
1. Select `1. Add Expense` from main menu
2. Choose category from the list
3. Enter amount (e.g., `50.00`)
4. Add optional description
5. Enter date or press Enter for today
6. System automatically checks budget and sends alerts if needed

#### Setting a Budget
1. Select `3. Manage Budgets` → `1. Set budget for category`
2. Choose category
3. Enter budget amount
4. Choose current month or specify month/year
5. Budget is saved and will be used for comparisons

#### Viewing Reports
1. Select `4. View Reports`
2. Choose report type:
   - `1. Monthly summary` - Shows total spending by category
   - `2. Budget vs Spending comparison` - Detailed budget analysis
3. Select month/year or use current month
4. View formatted tables with insights

#### Creating a Shared Expense Group
1. Select `6. Group Expenses` → `1. Create new group`
2. Enter group name and description
3. Select members from user list
4. Group is created and ready for shared expenses

#### Adding a Shared Expense
1. Select `6. Group Expenses` → `2. Add shared expense`
2. Choose group
3. Select category and enter amount
4. Choose equal split or custom amounts
5. System tracks who paid and calculates balances

---

## 🧪 Test Cases

### Test Case 1: User Registration and Login

**Objective**: Verify user can register and login

**Steps**:
1. Start application
2. Select `2. Register new user`
3. Enter username: `john_doe`
4. Enter email: `john@example.com`
5. System should confirm registration and auto-login

**Expected Result**: 
- ✅ User created successfully message
- ✅ Redirected to main menu
- ✅ Default alert settings created

---

### Test Case 2: Add Expense

**Objective**: Verify expense logging functionality

**Steps**:
1. Login as registered user
2. Select `1. Add Expense`
3. Choose category: `Food` (option 1)
4. Enter amount: `45.50`
5. Enter description: `Lunch at restaurant`
6. Press Enter for today's date

**Expected Result**:
- ✅ Success message: "Expense of $45.50 added to 'Food'!"
- ✅ Expense saved to database

**Validation Query**:
```sql
SELECT * FROM expenses WHERE user_id = 1 ORDER BY created_at DESC LIMIT 1;
```

---

### Test Case 3: Set Monthly Budget

**Objective**: Verify budget setting for categories

**Steps**:
1. Select `3. Manage Budgets` → `1. Set budget for category`
2. Choose category: `Food`
3. Enter amount: `500`
4. Select current month: `y`

**Expected Result**:
- ✅ Success message: "Budget for 'Food' set to $500.00!"
- ✅ Budget visible in budget list

**Validation Query**:
```sql
SELECT b.*, c.name FROM budgets b 
JOIN categories c ON b.category_id = c.id 
WHERE b.user_id = 1 AND EXTRACT(MONTH FROM CURRENT_DATE) = b.month;
```

---

### Test Case 4: Budget Alert Trigger

**Objective**: Verify automatic budget alerts

**Prerequisites**: Set Food budget to $100 for current month

**Steps**:
1. Add expense: Food, $95
2. Observe terminal output
3. Check email inbox (if configured)

**Expected Result**:
- ✅ Warning message in terminal: "Budget alert for Food! Only X% remaining..."
- ✅ Email received (if configured) with budget warning

**Edge Case**: Add another expense of $10 (total $105)
- ✅ Should show "Budget exceeded" message
- ✅ Email with exceeded notification

---

### Test Case 5: Different Budgets for Different Months

**Objective**: Verify monthly budget variations

**Steps**:
1. Set Transport budget for January 2024: $200
2. Set Transport budget for February 2024: $300
3. View budgets for January → should show $200
4. View budgets for February → should show $300

**Expected Result**:
- ✅ Each month maintains separate budget
- ✅ No conflicts or overwrites

**Validation Query**:
```sql
SELECT month, year, amount FROM budgets 
WHERE user_id = 1 AND category_id = (SELECT id FROM categories WHERE name = 'Transport')
ORDER BY year, month;
```

---

### Test Case 6: Custom Alert Threshold

**Objective**: Verify custom alert configuration

**Steps**:
1. Select `5. Manage Alerts` → `1. Set custom alert threshold`
2. Enter threshold: `20` (20% remaining)
3. Enable email: `y`
4. Set Food budget: $100
5. Add expense: $85 (15% remaining)

**Expected Result**:
- ✅ No alert yet (above 20% threshold)

**Continue**:
6. Add expense: $10 (5% remaining)

**Expected Result**:
- ✅ Alert triggered: "Only 5% remaining!"
- ✅ Email sent

---

### Test Case 7: Monthly Report

**Objective**: Verify report generation

**Prerequisites**: 
- Food expense: $120
- Transport expense: $80
- Entertainment expense: $50

**Steps**:
1. Select `4. View Reports` → `1. Monthly summary`
2. Choose current month

**Expected Result**:
- ✅ Total Spending: $250.00
- ✅ Category breakdown:
  - Food: $120.00 (48%)
  - Transport: $80.00 (32%)
  - Entertainment: $50.00 (20%)

---

### Test Case 8: Budget vs Spending Comparison

**Objective**: Verify budget comparison report

**Prerequisites**:
- Food budget: $100, spent: $120
- Transport budget: $150, spent: $80
- Entertainment budget: $75, spent: $50

**Steps**:
1. Select `4. View Reports` → `2. Budget vs Spending comparison`
2. Choose current month

**Expected Result**:
```
Category      | Budget    | Spent     | Remaining | Used %  | Status
Food          | $100.00   | $120.00   | -$20.00   | 120.0%  | ✗
Transport     | $150.00   | $80.00    | $70.00    | 53.3%   | ✓
Entertainment | $75.00    | $50.00    | $25.00    | 66.7%   | ✓
```

---

### Test Case 9: Group Creation and Shared Expense

**Objective**: Verify Splitwise-like functionality

**Prerequisites**: Create users: alice, bob, charlie

**Steps**:
1. Login as alice
2. Select `6. Group Expenses` → `1. Create new group`
3. Name: `Roommates`
4. Add bob and charlie as members
5. Select `2. Add shared expense`
6. Amount: $120 (dinner bill)
7. Split equally: `y`

**Expected Result**:
- ✅ Group created with 3 members
- ✅ Expense split: $40 each
- ✅ Alice paid $120, owes $40 (net: +$80)
- ✅ Bob owes $40 (net: -$40)
- ✅ Charlie owes $40 (net: -$40)

**Validation**:
```sql
SELECT u.username, es.amount, es.paid 
FROM expense_splits es
JOIN users u ON es.user_id = u.id
WHERE es.expense_id = 1;
```

---

### Test Case 10: Group Balance Calculation

**Objective**: Verify balance tracking

**Prerequisites**: Use group from Test Case 9

**Steps**:
1. Add another expense: Bob pays $90, split equally ($30 each)
2. Select `6. Group Expenses` → `3. View group balances`

**Expected Result**:
```
Member  | Total Paid | Total Owed | Net Balance | Status
Alice   | $120.00    | $70.00     | +$50.00     | Gets back
Bob     | $90.00     | $70.00     | +$20.00     | Gets back
Charlie | $0.00      | $70.00     | -$70.00     | Owes
```

---

### Test Case 11: Custom Category Creation

**Objective**: Verify custom category addition

**Steps**:
1. Select `7. Categories` → `2. Add new category`
2. Name: `Fitness`
3. Description: `Gym and sports expenses`

**Expected Result**:
- ✅ Category created
- ✅ Available in expense entry
- ✅ Can set budgets for it

---

### Test Case 12: View Expenses with Filters

**Objective**: Verify expense filtering

**Prerequisites**: Create multiple expenses across categories and months

**Steps**:
1. Select `2. View Expenses` → `2. View expenses for specific month`
2. Enter month: `11`, year: `2024`

**Expected Result**:
- ✅ Only November 2024 expenses shown
- ✅ Total calculated correctly

**Steps**:
3. Select `2. View Expenses` → `3. View expenses by category`
4. Choose `Food`

**Expected Result**:
- ✅ Only Food expenses shown across all months
- ✅ Total for Food category displayed

---

### Test Case 13: Edge Case - Zero Budget

**Objective**: Handle edge cases

**Steps**:
1. Try to set budget: $0

**Expected Result**:
- ✅ Error: "Budget amount must be a positive number"

---

### Test Case 14: Edge Case - Negative Amount

**Objective**: Validate input constraints

**Steps**:
1. Try to add expense: $-50

**Expected Result**:
- ✅ Error: "Amount must be a positive number"

---

### Test Case 15: Email Notification (Integration Test)

**Objective**: Verify email sending

**Prerequisites**: Configure email in .env

**Steps**:
1. Set budget: $100
2. Add expense: $95 (to trigger alert)
3. Check email inbox

**Expected Result**:
- ✅ Email received with:
  - Subject: "⚠️ Budget Alert: [Category]"
  - Budget summary table
  - Warning message

---

## 📊 Database Schema

### Entity Relationship Diagram

```
Users (1) ──< (M) Expenses
Users (1) ──< (M) Budgets
Users (1) ──< (M) Alerts
Users (M) ──< (M) Groups
Categories (1) ──< (M) Expenses
Categories (1) ──< (M) Budgets
Groups (1) ──< (M) Expenses
Expenses (1) ──< (M) ExpenseSplits
```

### Tables

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### categories
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### budgets
```sql
CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    category_id INTEGER REFERENCES categories(id) NOT NULL,
    amount DECIMAL(10,2) CHECK (amount > 0) NOT NULL,
    month INTEGER CHECK (month >= 1 AND month <= 12) NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category_id, month, year)
);
```

#### expenses
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    category_id INTEGER REFERENCES categories(id) NOT NULL,
    amount DECIMAL(10,2) CHECK (amount > 0) NOT NULL,
    description VARCHAR(200),
    date TIMESTAMP NOT NULL,
    group_id INTEGER REFERENCES groups(id),
    is_shared BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### groups
```sql
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    created_by INTEGER REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### expense_splits
```sql
CREATE TABLE expense_splits (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER REFERENCES expenses(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    amount DECIMAL(10,2) CHECK (amount >= 0) NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### alerts
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    threshold_percentage INTEGER CHECK (threshold_percentage >= 0 AND threshold_percentage <= 100) DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    email_notification BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📝 Code Documentation

### Architecture Overview

The application follows a **layered architecture**:

1. **Presentation Layer** (`main.py`): CLI interface
2. **Service Layer** (`services.py`): Business logic
3. **Data Access Layer** (`database.py`, `models.py`): Database operations
4. **External Services** (`email_service.py`): Email functionality
5. **Utilities** (`utils.py`, `config.py`): Helper functions and configuration

### Key Design Patterns

- **Repository Pattern**: Database access abstracted through service layer
- **Singleton**: Configuration management
- **Context Manager**: Database session handling
- **Service Layer**: Business logic separated from presentation

### Code Quality Features

- ✅ **Comprehensive docstrings**: Every function documented
- ✅ **Type hints**: Function parameters and returns typed
- ✅ **Error handling**: Try-catch blocks with meaningful messages
- ✅ **Input validation**: All user inputs validated
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM (parameterized queries)
- ✅ **Transaction Management**: Automatic commit/rollback
- ✅ **Code organization**: Single Responsibility Principle

### Module Documentation

#### models.py
```python
"""
Database models using SQLAlchemy ORM.
- User: Application users
- Category: Expense categories
- Budget: Monthly budget limits
- Expense: Individual expenses
- Group: Expense-sharing groups
- ExpenseSplit: Split calculations
- Alert: Budget alert settings
"""
```

#### services.py
```python
"""
Business logic layer.
Methods:
- create_user(): User registration
- add_expense(): Log new expense
- set_budget(): Configure budgets
- get_monthly_report(): Generate reports
- create_group(): Create sharing group
- add_shared_expense(): Split expenses
- _check_budget_alerts(): Auto alert checking
"""
```

#### email_service.py
```python
"""
Email notification service.
Uses SMTP for sending HTML emails.
Methods:
- send_budget_alert(): Warning emails
- send_budget_exceeded_alert(): Exceeded notifications
"""
```

---

## 🎓 Features Implementation

### 1. Daily Expense Logging ✅
**Implementation**: `services.py::add_expense()`
- Stores expense with amount, category, description, date
- Validates positive amounts
- Supports custom dates or defaults to today
- Triggers automatic budget checks

### 2. Expense Categories ✅
**Implementation**: `models.py::Category`, `services.py::create_category()`
- Pre-populated with 8 default categories
- Support for custom categories
- Used in budgets and expenses via foreign keys

### 3. Monthly Budgets ✅
**Implementation**: `services.py::set_budget()`
- Per-category budget limits
- Month and year specific
- Unique constraint ensures one budget per category/month/year
- Update existing or create new

### 4. Budget Alerts ✅
**Implementation**: `services.py::_check_budget_alerts()`
- Automatic check after each expense
- Terminal warnings with colored output
- Threshold-based (customizable %)
- Email notifications (optional)

### 5. Monthly Reports ✅
**Implementation**: `services.py::get_monthly_report()`
- Total spending calculation
- Category-wise breakdown
- Percentage distribution
- Budget vs actual comparison

### 6. Different Monthly Budgets ⭐
**Implementation**: `models.py::Budget` with month/year fields
- Unique constraint on (user, category, month, year)
- Query filters by month/year
- Historical budget tracking

### 7. Custom Alerts ⭐
**Implementation**: `models.py::Alert`, `services.py::set_custom_alert()`
- Configurable threshold percentage
- Category-specific or global
- Enable/disable email per alert
- Multiple alerts per user

### 8. Email Notifications ⭐
**Implementation**: `email_service.py::EmailService`
- SMTP integration (Gmail compatible)
- HTML formatted emails
- Budget summary tables in email
- Separate templates for warnings vs exceeded

### 9. Group Expense Sharing ⭐
**Implementation**: `models.py::Group, ExpenseSplit`, `services.py::add_shared_expense()`
- Create groups with multiple members
- Split expenses equally or custom
- Track who paid
- Calculate net balances (who owes whom)
- Splitwise-like balance settlement logic

---

## 🐳 Docker Commands Reference

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access application
docker exec -it expense_tracker_app python main.py

# Access database directly
docker exec -it expense_tracker_db psql -U expense_user -d expense_tracker

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (deletes data)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# View running containers
docker-compose ps
```

---

## 🔧 Troubleshooting

### Database Connection Error
```
Error: could not connect to server
```
**Solution**: Ensure PostgreSQL is running
```bash
# Docker
docker-compose up -d db

# Local
# Check PostgreSQL service is running
```

### Email Not Sending
```
Failed to send email: Authentication failed
```
**Solutions**:
1. Verify SMTP credentials in `.env`
2. Enable "Less secure app access" or use App Password (Gmail)
3. Check SMTP server and port

### Import Errors
```
ModuleNotFoundError: No module named 'sqlalchemy'
```
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

---

## 📈 Performance Considerations

- **Database Indexing**: Indexes on user_id, category_id, date columns
- **Query Optimization**: Uses SQLAlchemy's efficient query building
- **Session Management**: Context managers ensure proper cleanup
- **Lazy Loading**: Relationships loaded only when accessed

---

## 🔒 Security Features

- ✅ SQL Injection Prevention (ORM with parameterized queries)
- ✅ Input validation on all user inputs
- ✅ Email validation using regex
- ✅ Environment variables for sensitive data
- ✅ Password stored in environment (not hardcoded)
- ✅ Database constraints (CHECK, UNIQUE, FOREIGN KEY)

---

## 🤝 Contributing

This is an individual project for assessment purposes. Originality is maintained without ChatGPT-generated code snippets.

---

## 📄 License

This project is created for educational/assessment purposes.

---

## 👨‍💻 Author

Created as part of placement assessment assignment.

**Note**: All code written with individual effort, following Python best practices and coding standards.
