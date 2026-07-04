"""
Seed the SQLite database with realistic banking CRM data.
Creates tables: customers, transactions, products, customer_products, interaction_log
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta
from config import DB_PATH

# ---------------------------------------------------------------------------
# Data pools for realistic generation
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
    "Ayaan", "Krishna", "Ishaan", "Priya", "Ananya", "Diya", "Aditi",
    "Kiara", "Saanvi", "Aisha", "Meera", "Neha", "Pooja", "Rahul",
    "Amit", "Suresh", "Ravi", "Deepak", "Sunita", "Kavita", "Lakshmi",
    "Rajesh", "Manish"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Reddy",
    "Nair", "Joshi", "Mehta", "Iyer", "Rao", "Das", "Chatterjee",
    "Bose", "Pillai", "Malhotra", "Kapoor", "Banerjee", "Srivastava"
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
]

OCCUPATIONS = [
    "Software Engineer", "Doctor", "Business Owner", "Teacher",
    "CA (Chartered Accountant)", "Government Employee", "Architect",
    "Marketing Manager", "Consultant", "Retired Professional",
    "Lawyer", "Bank Manager", "Freelancer", "Sales Executive",
    "HR Manager"
]

SEGMENTS = ["Retail", "Premium", "HNI", "Ultra-HNI"]

PRODUCT_CATALOG = [
    {"product_id": "PL001", "name": "Personal Loan", "category": "Loan",
     "min_income": 300000, "min_balance": 50000,
     "description": "Unsecured personal loan up to 40L at competitive rates"},
    {"product_id": "HL001", "name": "Home Loan", "category": "Loan",
     "min_income": 500000, "min_balance": 100000,
     "description": "Home loan up to 5Cr with flexible tenure"},
    {"product_id": "CC001", "name": "Premium Credit Card", "category": "Card",
     "min_income": 600000, "min_balance": 75000,
     "description": "Premium credit card with lounge access and reward points"},
    {"product_id": "FD001", "name": "Fixed Deposit", "category": "Deposit",
     "min_income": 0, "min_balance": 25000,
     "description": "Fixed deposit with up to 7.5% interest rate"},
    {"product_id": "MF001", "name": "Mutual Fund SIP", "category": "Investment",
     "min_income": 300000, "min_balance": 50000,
     "description": "Curated mutual fund SIPs with auto-debit facility"},
    {"product_id": "INS01", "name": "Term Life Insurance", "category": "Insurance",
     "min_income": 250000, "min_balance": 30000,
     "description": "Term insurance cover up to 2Cr at affordable premiums"},
    {"product_id": "GL001", "name": "Gold Loan", "category": "Loan",
     "min_income": 150000, "min_balance": 20000,
     "description": "Instant gold loan with minimal documentation"},
    {"product_id": "BL001", "name": "Business Loan", "category": "Loan",
     "min_income": 500000, "min_balance": 200000,
     "description": "Collateral-free business loan up to 50L"},
]

TRANSACTION_CATEGORIES = [
    "Salary Credit", "EMI Payment", "UPI Transfer", "Online Shopping",
    "Utility Bill", "Insurance Premium", "Investment", "ATM Withdrawal",
    "Rent Payment", "Medical Expense", "Travel", "Dining",
    "Education Fee", "Subscription", "Loan Disbursement"
]


def _random_phone():
    return f"+91-{random.randint(70000, 99999)}{random.randint(10000, 99999)}"


def _random_email(first, last):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(domains)}"


def _random_date(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed_database(force: bool = False):
    """Create tables and populate with synthetic data."""

    if os.path.exists(DB_PATH) and not force:
        return  # Already seeded

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    cur.executescript("""
    DROP TABLE IF EXISTS interaction_log;
    DROP TABLE IF EXISTS customer_products;
    DROP TABLE IF EXISTS transactions;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;

    CREATE TABLE customers (
        customer_id     TEXT PRIMARY KEY,
        first_name      TEXT NOT NULL,
        last_name       TEXT NOT NULL,
        age             INTEGER,
        gender          TEXT,
        city            TEXT,
        occupation      TEXT,
        annual_income   REAL,
        account_balance REAL,
        credit_score    INTEGER,
        segment         TEXT,
        relationship_vintage_years REAL,
        phone           TEXT,
        email           TEXT,
        last_contacted  TEXT,
        is_active       INTEGER DEFAULT 1
    );

    CREATE TABLE products (
        product_id      TEXT PRIMARY KEY,
        name            TEXT NOT NULL,
        category        TEXT,
        min_income      REAL,
        min_balance     REAL,
        description     TEXT
    );

    CREATE TABLE transactions (
        txn_id          TEXT PRIMARY KEY,
        customer_id     TEXT,
        txn_date        TEXT,
        amount          REAL,
        category        TEXT,
        txn_type        TEXT,   -- credit / debit
        channel         TEXT,   -- UPI / NetBanking / Branch / ATM
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE customer_products (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     TEXT,
        product_id      TEXT,
        enrolled_date   TEXT,
        status          TEXT DEFAULT 'active',
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );

    CREATE TABLE interaction_log (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id     TEXT,
        interaction_type TEXT,  -- call / email / whatsapp / branch_visit
        summary         TEXT,
        interaction_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """)

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------
    for p in PRODUCT_CATALOG:
        cur.execute(
            "INSERT INTO products VALUES (?,?,?,?,?,?)",
            (p["product_id"], p["name"], p["category"],
             p["min_income"], p["min_balance"], p["description"])
        )

    # ------------------------------------------------------------------
    # Customers (50 realistic profiles)
    # ------------------------------------------------------------------
    random.seed(42)
    customers = []
    for i in range(1, 51):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        age = random.randint(23, 65)
        gender = random.choice(["M", "F"])
        city = random.choice(CITIES)
        occupation = random.choice(OCCUPATIONS)

        # Income influenced by segment
        segment = random.choices(SEGMENTS, weights=[50, 30, 15, 5])[0]
        if segment == "Retail":
            income = random.randint(200000, 800000)
        elif segment == "Premium":
            income = random.randint(800000, 2000000)
        elif segment == "HNI":
            income = random.randint(2000000, 10000000)
        else:
            income = random.randint(10000000, 50000000)

        balance = random.randint(int(income * 0.05), int(income * 0.8))
        credit_score = random.randint(580, 900)
        vintage = round(random.uniform(0.5, 20.0), 1)
        phone = _random_phone()
        email = _random_email(first, last)

        days_since_contact = random.randint(1, 365)
        last_contacted = (datetime.now() - timedelta(days=days_since_contact)).strftime("%Y-%m-%d")

        cid = f"CUST{i:04d}"
        customers.append(cid)

        cur.execute(
            "INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cid, first, last, age, gender, city, occupation,
             income, balance, credit_score, segment, vintage,
             phone, email, last_contacted, 1)
        )

    # ------------------------------------------------------------------
    # Transactions (15-40 per customer, last 6 months)
    # ------------------------------------------------------------------
    txn_counter = 0
    for cid in customers:
        n_txns = random.randint(15, 40)
        for _ in range(n_txns):
            txn_counter += 1
            txn_id = f"TXN{txn_counter:06d}"
            days_ago = random.randint(0, 180)
            txn_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            category = random.choice(TRANSACTION_CATEGORIES)

            if category == "Salary Credit":
                amount = random.randint(20000, 500000)
                txn_type = "credit"
            elif category in ("EMI Payment", "Insurance Premium", "Rent Payment"):
                amount = random.randint(5000, 80000)
                txn_type = "debit"
            elif category == "Loan Disbursement":
                amount = random.randint(100000, 2000000)
                txn_type = "credit"
            else:
                amount = random.randint(200, 50000)
                txn_type = random.choice(["credit", "debit"])

            channel = random.choice(["UPI", "NetBanking", "Branch", "ATM", "POS"])

            cur.execute(
                "INSERT INTO transactions VALUES (?,?,?,?,?,?,?)",
                (txn_id, cid, txn_date, amount, category, txn_type, channel)
            )

    # ------------------------------------------------------------------
    # Customer-Product enrolments (1-3 per customer)
    # ------------------------------------------------------------------
    for cid in customers:
        n_products = random.randint(1, 3)
        enrolled = random.sample(PRODUCT_CATALOG, n_products)
        for p in enrolled:
            date = _random_date(2021, 2025).strftime("%Y-%m-%d")
            cur.execute(
                "INSERT INTO customer_products (customer_id, product_id, enrolled_date, status) VALUES (?,?,?,?)",
                (cid, p["product_id"], date, random.choice(["active", "active", "closed"]))
            )

    # ------------------------------------------------------------------
    # Interaction log (0-5 per customer)
    # ------------------------------------------------------------------
    for cid in customers:
        n_interactions = random.randint(0, 5)
        for _ in range(n_interactions):
            itype = random.choice(["call", "email", "whatsapp", "branch_visit"])
            summaries = [
                "Discussed savings account benefits",
                "Customer enquired about personal loan rates",
                "Follow-up on credit card application",
                "Customer requested account statement",
                "Pitched mutual fund SIP options",
                "Resolved complaint about failed transaction",
                "Customer interested in home loan pre-approval",
                "Birthday greeting call",
                "Cross-sell attempt for insurance",
                "Customer asked about FD renewal rates",
            ]
            summary = random.choice(summaries)
            idate = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
            cur.execute(
                "INSERT INTO interaction_log (customer_id, interaction_type, summary, interaction_date) VALUES (?,?,?,?)",
                (cid, itype, summary, idate)
            )

    conn.commit()
    conn.close()
    print(f"Database seeded at {DB_PATH} with 50 customers.")


if __name__ == "__main__":
    seed_database(force=True)
