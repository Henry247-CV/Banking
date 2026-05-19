"""
Savings History Service — Đăng Khoa Bank
Handles retrieval and formatting of savings-related transactions for both user and admin views.
"""

from src.database.database import get_db_connection

class SavingsHistoryService:
    @staticmethod
    def get_user_savings_history(username: str, limit: int = 50) -> list:
        """Retrieves all savings transactions for a specific user across all plans."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT st.*, sa.plan_name, sa.savings_type 
                FROM savings_transactions st
                JOIN savings_accounts sa ON st.savings_id = sa.savings_id
                WHERE sa.username = ?
                ORDER BY st.created_at DESC
                LIMIT ?
            """, (username, limit))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"SavingsHistoryService.get_user_savings_history error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_all_savings_history(limit: int = 100) -> list:
        """Retrieves all savings transactions for admin monitoring."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT st.*, sa.username, sa.plan_name, sa.savings_type 
                FROM savings_transactions st
                JOIN savings_accounts sa ON st.savings_id = sa.savings_id
                ORDER BY st.created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"SavingsHistoryService.get_all_savings_history error: {e}")
            return []
        finally:
            conn.close()
