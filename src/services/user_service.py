from src.database.database import get_db_connection
from src.services.notification_service import NotificationService
from src.services.tier_service import TierService
import sqlite3

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """Retrieves a user's full data by their ID."""
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            return dict(user_row) if user_row else None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_username(username):
        """Retrieves a user's full data by their username."""
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            if user_row:
                user_data = dict(user_row)
                # Auto-update tier if needed
                TierService.update_user_tier(username, user_data['balance'])
                
                # Fetch again to get updated tier if it was changed
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user_row = cursor.fetchone()
                return dict(user_row) if user_row else None
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_phone(phone):
        """Retrieves a user's data by their phone number."""
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            user_row = cursor.fetchone()
            return dict(user_row) if user_row else None
        finally:
            conn.close()

    @staticmethod
    def update_user_profile(user_id, username, full_name, phone, email):
        """Updates a user's profile information."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET full_name = ?, phone = ?, email = ? WHERE id = ?",
                (full_name, phone, email, user_id)
            )
            conn.commit()
            NotificationService.create_notification(
                username,
                "Profile Updated",
                "Your personal information has been updated successfully.",
                "INFO"
            )
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_balance(user_id):
        """Retrieves a user's current balance."""
        conn = get_db_connection()
        if not conn: return 0.0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0.0
        finally:
            conn.close()

    @staticmethod
    def refresh_user_data(username):
        """Fetches the latest user data and ensures tier is correct."""
        return UserService.get_user_by_username(username)
