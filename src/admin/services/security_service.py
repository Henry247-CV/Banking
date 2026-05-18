import sqlite3
import uuid
from datetime import datetime, timedelta
from src.database.database import get_db_connection

class SecurityService:
    @staticmethod
    def log_admin_action(admin_username, action, target):
        """Logs an administrative action to the audit trail."""
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admin_logs (admin_username, action, target) VALUES (?, ?, ?)",
                (admin_username, action, target)
            )
            conn.commit()
        except Exception as e:
            print(f"Error logging admin action: {e}")
        finally:
            conn.close()

    @staticmethod
    def track_login_attempt(username, status, device="Desktop App", location="Local"):
        """Records a login attempt (SUCCESS, FAILED, BLOCKED)."""
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO login_history (username, status, device, location) VALUES (?, ?, ?, ?)",
                (username, status, device, location)
            )
            conn.commit()
        except Exception as e:
            print(f"Error tracking login attempt: {e}")
        finally:
            conn.close()

    @staticmethod
    def get_login_history(limit=50):
        """Returns the most recent login attempts."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, login_time, status, device, location FROM login_history ORDER BY login_time DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting login history: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_admin_logs(limit=50):
        """Returns the most recent admin activity logs."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT admin_username, action, target, created_at FROM admin_logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting admin logs: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def create_session(username):
        """Creates a new active session and returns the token."""
        token = str(uuid.uuid4())
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO active_sessions (username, session_token, status) VALUES (?, ?, 'ACTIVE')",
                (username, token)
            )
            conn.commit()
            return token
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_active_sessions():
        """Returns all active sessions."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, session_token, created_at FROM active_sessions WHERE status = 'ACTIVE' ORDER BY created_at DESC"
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def terminate_session(session_id):
        """Removes an active session."""
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM active_sessions WHERE id = ?", (session_id,))
            conn.commit()
        except Exception as e:
            print(f"Error terminating session: {e}")
        finally:
            conn.close()

    @staticmethod
    def get_security_overview_stats():
        """Aggregates stats for the security overview dashboard."""
        stats = {
            "active_sessions": 0,
            "failed_logins": 0,
            "failed_today": 0,
            "frozen_accounts": 0
        }
        conn = get_db_connection()
        if not conn: return stats
        try:
            cursor = conn.cursor()
            
            # Active Sessions
            cursor.execute("SELECT COUNT(*) FROM active_sessions WHERE status = 'ACTIVE'")
            stats["active_sessions"] = cursor.fetchone()[0]
            
            # Failed Logins (Total)
            cursor.execute("SELECT COUNT(*) FROM login_history WHERE status = 'FAILED'")
            stats["failed_logins"] = cursor.fetchone()[0]
            
            # Failed Logins (Today)
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM login_history WHERE status = 'FAILED' AND login_time LIKE ?", (f"{today}%",))
            stats["failed_today"] = cursor.fetchone()[0]
            
            # Frozen/Suspended Accounts
            cursor.execute("SELECT COUNT(*) FROM users WHERE account_status IN ('FROZEN', 'SUSPENDED')")
            stats["frozen_accounts"] = cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            print(f"Error getting security stats: {e}")
            return stats
        finally:
            conn.close()

    @staticmethod
    def detect_suspicious_activity():
        """Runs simple rules to detect suspicious login patterns."""
        alerts = []
        conn = get_db_connection()
        if not conn: return alerts
        try:
            cursor = conn.cursor()
            
            # Rule 1: High Risk - 5+ failed logins for a user in last 24h
            day_ago = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                SELECT username, COUNT(*) as fail_count 
                FROM login_history 
                WHERE status = 'FAILED' AND login_time > ? 
                GROUP BY username 
                HAVING fail_count >= 5
            """, (day_ago,))
            
            for row in cursor.fetchall():
                alerts.append({
                    "type": "CRITICAL",
                    "title": "Brute Force Detected",
                    "desc": f"User '{row[0]}' has {row[1]} failed login attempts in 24h."
                })
                
            # Rule 2: Medium Risk - Multiple rapid login attempts (3+ in 5 mins)
            five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                SELECT username, COUNT(*) as try_count 
                FROM login_history 
                WHERE login_time > ? 
                GROUP BY username 
                HAVING try_count >= 3
            """, (five_mins_ago,))
            
            for row in cursor.fetchall():
                # Avoid duplicate alerts for the same user if already CRITICAL
                if not any(a["desc"].startswith(f"User '{row[0]}'") for a in alerts):
                    alerts.append({
                        "type": "WARNING",
                        "title": "Rapid Login Activity",
                        "desc": f"Multiple login attempts detected for '{row[0]}' in last 5 mins."
                    })

            # Rule 3: Suspicious Transfers (Placeholder for future)
            # cursor.execute("SELECT COUNT(*) FROM transactions WHERE flagged = 1")
            # ...
            
            return alerts
        except Exception as e:
            print(f"Error detecting suspicious activity: {e}")
            return alerts
        finally:
            conn.close()
