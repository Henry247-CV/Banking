"""
Savings Analytics Service — Đăng Khoa Bank
Processes savings data into formats suitable for chart rendering and dashboard metrics.
"""

from src.database.database import get_db_connection
from datetime import datetime, timedelta

class SavingsAnalyticsService:
    @staticmethod
    def get_growth_data(username: str) -> list:
        """Retrieves cumulative savings growth over the last 6 months."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            # Simplified growth: just get current balance per plan for now
            # In a real app, we'd query history to rebuild balance over time
            cursor.execute("""
                SELECT plan_name, current_amount 
                FROM savings_accounts 
                WHERE username = ? AND status = 'ACTIVE'
            """, (username,))
            return [(row["plan_name"], row["current_amount"]) for row in cursor.fetchall()]
        except Exception as e:
            print(f"SavingsAnalyticsService.get_growth_data error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_monthly_deposits(username: str) -> list:
        """Retrieves monthly deposit totals for the current user."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%m', created_at) as month, SUM(amount) as total
                FROM savings_transactions st
                JOIN savings_accounts sa ON st.savings_id = sa.savings_id
                WHERE sa.username = ? AND st.transaction_type = 'DEPOSIT'
                GROUP BY month
                ORDER BY month ASC
            """, (username,))
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            data = []
            results = {row["month"]: row["total"] for row in cursor.fetchall()}
            for i in range(1, 13):
                m_str = f"{i:02d}"
                data.append((months[i-1], results.get(m_str, 0.0)))
            return data
        except Exception as e:
            print(f"SavingsAnalyticsService.get_monthly_deposits error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_admin_savings_metrics() -> dict:
        """Retrieves global savings metrics for the admin dashboard."""
        conn = get_db_connection()
        if not conn:
            return {}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(current_amount) as total_saved, COUNT(*) as total_plans FROM savings_accounts WHERE status = 'ACTIVE'")
            row = cursor.fetchone()
            
            cursor.execute("SELECT SUM(amount) as total_withdrawals FROM savings_transactions WHERE transaction_type = 'WITHDRAWAL'")
            w_row = cursor.fetchone()
            
            return {
                "total_savings_volume": float(row["total_saved"] or 0),
                "active_savings_accounts": int(row["total_plans"] or 0),
                "total_withdrawals": float(w_row["total_withdrawals"] or 0)
            }
        except Exception as e:
            print(f"SavingsAnalyticsService.get_admin_savings_metrics error: {e}")
            return {}
        finally:
            conn.close()
