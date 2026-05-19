import sys
import os

# Allow absolute imports from 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.database import get_db_connection

class AccountLookupService:
    @staticmethod
    def find_user_by_phone(phone: str) -> dict | None:
        """Finds a user by their registered phone number."""
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def find_user_by_account(account_number: str) -> dict | None:
        """Tìm kiếm người dùng bằng số tài khoản nội bộ."""
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE account_number = ?", (account_number,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def validate_receiver(account_info: str) -> dict | None:
        """
        Validates a receiver by phone or account number.
        Returns user data if valid, None otherwise.
        """
        user = AccountLookupService.find_user_by_phone(account_info)
        if not user:
            user = AccountLookupService.find_user_by_account(account_info)
        return user
ce.find_user_by_account(account_info)
        return user
