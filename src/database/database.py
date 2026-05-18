import sqlite3
import os
from datetime import datetime

DB_PATH = "bank.db"

def init_db():
    """Initializes the database and creates all required tables with safe migrations."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            phone TEXT,
            cccd TEXT UNIQUE,
            email TEXT,
            account_number TEXT UNIQUE,
            balance REAL DEFAULT 10000000.0,
            customer_tier TEXT DEFAULT 'STANDARD',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 2. Transactions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_username TEXT NOT NULL,
            receiver_bank TEXT NOT NULL,
            receiver_account TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT,
            status TEXT DEFAULT 'SUCCESS',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 3. Notifications Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT,
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 4. Savings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            goal_name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 5. Admin Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_username TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 6. Login History
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            device TEXT,
            location TEXT
        )
        """)

        # 7. Active Sessions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'ACTIVE'
        )
        """)

        # Safe migrations: Check for missing columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        column_updates = {
            "full_name": "TEXT",
            "phone": "TEXT",
            "cccd": "TEXT UNIQUE",
            "email": "TEXT",
            "account_number": "TEXT UNIQUE",
            "balance": "REAL DEFAULT 10000000.0",
            "customer_tier": "TEXT DEFAULT 'STANDARD'",
            "account_status": "TEXT DEFAULT 'ACTIVE'",
            "last_login": "DATETIME"
        }
        
        for col, col_type in column_updates.items():
            if col not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"Migration notice: {e}")

        # Migration: Ensure Account Number = Phone Number for all users
        cursor.execute("UPDATE users SET account_number = phone WHERE account_number LIKE 'DKB%'")

        # Safe migrations: transactions table columns
        cursor.execute("PRAGMA table_info(transactions)")
        txn_columns = [column[1] for column in cursor.fetchall()]

        txn_column_updates = {
            "flagged": "INTEGER DEFAULT 0",
            "risk_level": "TEXT DEFAULT 'LOW'",
            "review_status": "TEXT DEFAULT 'COMPLETED'",
        }

        for col, col_type in txn_column_updates.items():
            if col not in txn_columns:
                try:
                    cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"Transaction migration notice: {e}")

        # Insert default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, full_name, phone, cccd, account_number, balance, customer_tier, account_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("admin", "admin123", "System Administrator", "0000000000", "000000000000", "0000000000", 10000000.0, "STANDARD", "ACTIVE")
            )
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Returns a connection to the sqlite database with optimized settings."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None
