"""Analytics Service — Lightweight SQLite-based analytics for admin dashboard.

Provides aggregated statistics: user growth, transaction volumes, tier/risk
distribution, system health, and recent activity logs.
"""

from src.database.database import get_db_connection
from datetime import datetime


class AnalyticsService:
    """Service layer for admin analytics queries — all SQLite-based, no external deps."""

    @staticmethod
    def get_total_users():
        conn = get_db_connection()
        if not conn: return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_total_balance():
        conn = get_db_connection()
        if not conn: return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(balance), 0) FROM users")
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_transaction_volume(days=30):
        """Get transaction count within last N days."""
        conn = get_db_connection()
        if not conn: return 0
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM transactions "
                "WHERE created_at >= datetime('now', ?)",
                (f"-{days} days",)
            )
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_transaction_total_amount(days=30):
        """Get total transaction amount within last N days."""
        conn = get_db_connection()
        if not conn: return 0
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM transactions "
                "WHERE created_at >= datetime('now', ?)",
                (f"-{days} days",)
            )
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_tier_distribution():
        """Get user count per tier. Returns dict: {'STANDARD': N, 'GOLD': N, 'DIAMOND': N}."""
        conn = get_db_connection()
        if not conn: return {"STANDARD": 0, "GOLD": 0, "DIAMOND": 0}
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT customer_tier, COUNT(*) FROM users "
                "GROUP BY customer_tier"
            )
            result = {"STANDARD": 0, "GOLD": 0, "DIAMOND": 0}
            for row in cursor.fetchall():
                tier = str(row[0]) if row[0] else "STANDARD"
                result[tier] = row[1]
            return result
        except Exception:
            return {"STANDARD": 0, "GOLD": 0, "DIAMOND": 0}
        finally:
            conn.close()

    @staticmethod
    def get_risk_distribution():
        """Get transaction count per risk level."""
        conn = get_db_connection()
        if not conn: return {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT risk_level, COUNT(*) FROM transactions GROUP BY risk_level"
            )
            result = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
            for row in cursor.fetchall():
                level = str(row[0]) if row[0] else "LOW"
                if level in result:
                    result[level] = row[1]
            return result
        except Exception:
            return {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        finally:
            conn.close()

    @staticmethod
    def get_daily_transaction_counts(days=7):
        """Get daily transaction counts for last N days.
        Returns list of (date_str, count) tuples, oldest first.
        """
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DATE(created_at) as day, COUNT(*) "
                "FROM transactions "
                "WHERE created_at >= datetime('now', ?) "
                "GROUP BY day ORDER BY day ASC",
                (f"-{days} days",)
            )
            return [(str(row[0]), row[1]) for row in cursor.fetchall()]
        except Exception:
            return []
        finally:
            conn.close()

    @staticmethod
    def get_daily_user_registrations(days=7):
        """Get daily user registration counts for last N days."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DATE(created_at) as day, COUNT(*) "
                "FROM users "
                "WHERE created_at >= datetime('now', ?) "
                "GROUP BY day ORDER BY day ASC",
                (f"-{days} days",)
            )
            return [(str(row[0]), row[1]) for row in cursor.fetchall()]
        except Exception:
            return []
        finally:
            conn.close()

    @staticmethod
    def get_risk_statistics():
        """Get fraud monitoring overview stats."""
        conn = get_db_connection()
        if not conn:
            return {"flagged": 0, "critical": 0, "blocked": 0, "suspicious_users": 0}
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM transactions WHERE flagged = 1")
            flagged = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE risk_level IN ('HIGH', 'CRITICAL')"
            )
            critical = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE review_status = 'BLOCKED'"
            )
            blocked = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(DISTINCT sender_username) FROM transactions WHERE flagged = 1"
            )
            suspicious_users = cursor.fetchone()[0]

            return {
                "flagged": flagged,
                "critical": critical,
                "blocked": blocked,
                "suspicious_users": suspicious_users,
            }
        except Exception:
            return {"flagged": 0, "critical": 0, "blocked": 0, "suspicious_users": 0}
        finally:
            conn.close()

    @staticmethod
    def get_account_status_distribution():
        """Get user count per account status."""
        conn = get_db_connection()
        if not conn: return {"ACTIVE": 0, "FROZEN": 0, "SUSPENDED": 0}
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT account_status, COUNT(*) FROM users GROUP BY account_status"
            )
            result = {"ACTIVE": 0, "FROZEN": 0, "SUSPENDED": 0}
            for row in cursor.fetchall():
                status = str(row[0]) if row[0] else "ACTIVE"
                if status in result:
                    result[status] = row[1]
            return result
        except Exception:
            return {"ACTIVE": 0, "FROZEN": 0, "SUSPENDED": 0}
        finally:
            conn.close()

    @staticmethod
    def get_recent_activity(limit=10):
        """Get recent system activity (transfers, flagged events).
        Returns list of dicts with type, description, timestamp.
        """
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            activities = []

            # Recent transactions
            cursor.execute(
                "SELECT sender_username, receiver_account, amount, created_at, flagged "
                "FROM transactions ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            for row in cursor.fetchall():
                amount = f"{abs(float(row[2])):,.0f}" if row[2] else "0"
                flagged = bool(row[4])
                act_type = "🚩 FLAGGED" if flagged else "💸 Transfer"
                activities.append({
                    "type": act_type,
                    "desc": f"{row[0]} → {row[1]} : {amount} VND",
                    "time": str(row[3])[:16] if row[3] else "N/A",
                })

            return activities[:limit]
        except Exception:
            return []
        finally:
            conn.close()

    @staticmethod
    def get_system_health():
        """Get system health indicators."""
        conn = get_db_connection()
        if not conn:
            return {"db_status": "OFFLINE", "total_records": 0}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            users = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM transactions")
            txns = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM notifications")
            notifs = cursor.fetchone()[0]

            from src.core.theme_manager import ThemeManager
            from src.core.language_manager import LanguageManager

            return {
                "db_status": "ONLINE",
                "total_users": users,
                "total_transactions": txns,
                "total_notifications": notifs,
                "total_records": users + txns + notifs,
                "current_theme": ThemeManager().current_theme.title(),
                "current_language": LanguageManager().current_language.upper(),
            }
        except Exception:
            return {"db_status": "ERROR", "total_records": 0}
        finally:
            conn.close()
