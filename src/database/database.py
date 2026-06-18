import sqlite3
import os
from datetime import datetime

# DB_PATH will always be resolved relative to the 'BankingApp' root directory (parent of src)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bank.db"))

def init_db():
    """Initializes the database and creates all required tables with safe migrations."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20)
        cursor = conn.cursor()
        
        # Optimize for concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")

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
            username TEXT, -- Specific user if needed
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'INFO',
            priority TEXT DEFAULT 'LOW',
            target TEXT DEFAULT 'ALL_USERS',
            is_read INTEGER DEFAULT 0,
            created_by TEXT DEFAULT 'SYSTEM',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Safe migrations: notifications table columns
        cursor.execute("PRAGMA table_info(notifications)")
        notif_columns = [column[1] for column in cursor.fetchall()]

        notif_column_updates = {
            "priority": "TEXT DEFAULT 'LOW'",
            "target": "TEXT DEFAULT 'ALL_USERS'",
            "created_by": "TEXT DEFAULT 'SYSTEM'",
        }

        for col, col_type in notif_column_updates.items():
            if col not in notif_columns:
                try:
                    cursor.execute(f"ALTER TABLE notifications ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"Notification migration notice: {e}")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            plan_name TEXT NOT NULL,
            savings_type TEXT DEFAULT 'FLEXIBLE', -- FLEXIBLE or FIXED
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            interest_rate REAL DEFAULT 0.05,
            duration_months INTEGER DEFAULT 12,
            start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_date DATETIME,
            status TEXT DEFAULT 'ACTIVE', -- ACTIVE, COMPLETED, LOCKED, CANCELLED
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            savings_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            type TEXT NOT NULL, -- DEPOSIT, WITHDRAWAL, INTEREST
            amount REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (savings_id) REFERENCES savings_accounts (id)
        )
        """)

        # Safe migrations: savings_accounts table columns
        cursor.execute("PRAGMA table_info(savings_accounts)")
        savings_columns = [column[1] for column in cursor.fetchall()]

        # Migration: Rename savings_id to id if it exists (legacy schema)
        if "savings_id" in savings_columns and "id" not in savings_columns:
            try:
                cursor.execute("ALTER TABLE savings_accounts RENAME COLUMN savings_id TO id")
                print("Migration: Renamed savings_accounts.savings_id to id")
                # Refresh columns list
                cursor.execute("PRAGMA table_info(savings_accounts)")
                savings_columns = [column[1] for column in cursor.fetchall()]
            except sqlite3.OperationalError as e:
                print(f"Savings migration error (rename): {e}")

        savings_column_updates = {
            "interest_earned": "REAL DEFAULT 0",
            "last_growth_update": "DATETIME",
        }

        for col, col_type in savings_column_updates.items():
            if col not in savings_columns:
                try:
                    cursor.execute(f"ALTER TABLE savings_accounts ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"Savings migration notice: {e}")

        # Safe migrations: savings_transactions table columns
        cursor.execute("PRAGMA table_info(savings_transactions)")
        st_columns = [column[1] for column in cursor.fetchall()]
        
        # Migration: Rename transaction_type to type if it exists
        if "transaction_type" in st_columns and "type" not in st_columns:
            try:
                cursor.execute("ALTER TABLE savings_transactions RENAME COLUMN transaction_type TO type")
                print("Migration: Renamed savings_transactions.transaction_type to type")
                # Refresh columns
                cursor.execute("PRAGMA table_info(savings_transactions)")
                st_columns = [column[1] for column in cursor.fetchall()]
            except sqlite3.OperationalError as e:
                print(f"Savings transactions migration error (rename): {e}")

        if "username" not in st_columns:
            try:
                cursor.execute("ALTER TABLE savings_transactions ADD COLUMN username TEXT")
                print("Migration: Added username column to savings_transactions")
                # Backfill username from savings_accounts
                cursor.execute("""
                    UPDATE savings_transactions 
                    SET username = (SELECT username FROM savings_accounts WHERE savings_accounts.id = savings_transactions.savings_id)
                    WHERE username IS NULL
                """)
            except sqlite3.OperationalError as e:
                print(f"Savings transactions migration notice: {e}")

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

        # 8. System Settings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Insert default maintenance mode if not exists
        cursor.execute("SELECT * FROM system_settings WHERE key = 'maintenance_mode'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO system_settings (key, value) VALUES (?, ?)",
                ("maintenance_mode", "false")
            )

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
            "last_login": "DATETIME",
            "security_pin": "TEXT",
            "failed_attempts": "INTEGER DEFAULT 0",
            "last_failed_attempt": "DATETIME",
            "account_locked_until": "DATETIME"
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
        conn = sqlite3.connect(DB_PATH, timeout=20)
        conn.row_factory = sqlite3.Row
        
        # Ensure WAL mode is active for each connection for max concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None
