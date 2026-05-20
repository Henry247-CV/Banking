from src.database.database import get_db_connection
from datetime import datetime, timedelta

class SavingsAnalyticsService:
    @staticmethod
    def get_growth_data(username, days=7):
        """Returns a list of daily total savings for the last X days."""
        conn = get_db_connection()
        if not conn: return [0] * days
        try:
            cursor = conn.cursor()
            data = []
            for i in range(days - 1, -1, -1):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                cursor.execute("""
                    SELECT SUM(amount) FROM savings_transactions 
                    WHERE username = ? AND date(created_at) <= date(?)
                    AND type IN ('DEPOSIT', 'INTEREST')
                """, (username, date))
                total = cursor.fetchone()[0] or 0
                
                # Also subtract withdrawals
                cursor.execute("""
                    SELECT SUM(amount) FROM savings_transactions 
                    WHERE username = ? AND date(created_at) <= date(?)
                    AND type = 'WITHDRAWAL'
                """, (username, date))
                withdrawals = cursor.fetchone()[0] or 0
                
                data.append(max(0, total - withdrawals))
            return data
        except Exception:
            return [0] * days
        finally:
            conn.close()

    @staticmethod
    def get_monthly_deposits(username):
        """Returns monthly deposit volume."""
        conn = get_db_connection()
        if not conn: return 0
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount) FROM savings_transactions 
                WHERE username = ? AND type = 'DEPOSIT'
                AND strftime('%m', created_at) = strftime('%m', 'now')
            """, (username,))
            return cursor.fetchone()[0] or 0
        finally:
            conn.close()
