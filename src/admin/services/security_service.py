"""Security Service — Lightweight SQLite-based security operations for admin panel.

Provides:
- Admin activity logging
- Login history tracking
- Suspicious activity detection
- Active session management
"""

import uuid
from datetime import datetime, timedelta
from src.database.database import get_db_connection


class SecurityService:
    """Service layer for security and audit logging."""

    @staticmethod
    def log_admin_action(admin_username, action, target=None):
        """Log an administrative action."""
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
            print(f"Log admin action error: {e}")
        finally:
            conn.close()

    @staticmethod
    def track_login_attempt(username, status, device="Desktop App", location="Local"):
        """Record a login attempt."""
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
            print(f"Track login error: {e}")
        finally:
            conn.close()

    @staticmethod
    def create_session(username):
        """Create a new active session and return the token."""
        token = str(uuid.uuid4())
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO active_sessions (username, session_token) VALUES (?, ?)",
                (username, token)
            )
            conn.commit()
            return token
        except Exception as e:
            print(f"Create session error: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def terminate_session(session_id):
        """Terminate a session by ID."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE active_sessions SET status = 'TERMINATED' WHERE id = ?",
                (session_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Terminate session error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_login_history(limit=50):
        """Get recent login history."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, login_time, status, device, location "
                "FROM login_history ORDER BY login_time DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Get login history error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_active_sessions():
        """Get all currently active sessions."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, session_token, created_at "
                "FROM active_sessions WHERE status = 'ACTIVE' ORDER BY created_at DESC"
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Get active sessions error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_admin_logs(limit=50):
        """Get recent admin activity logs."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT admin_username, action, target, created_at "
                "FROM admin_logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Get admin logs error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def detect_suspicious_activity():
        """Analyze login history for suspicious patterns.
        
        Rules:
        - HIGH RISK: >= 5 failed logins within last hour
        - MEDIUM RISK: >= 3 failed logins within last hour
        """
        conn = get_db_connection()
        if not conn: return []
        
        alerts = []
        try:
            cursor = conn.cursor()
            
            # Find users with multiple recent failures
            cursor.execute(
                "SELECT username, COUNT(*) as fail_count "
                "FROM login_history "
                "WHERE status = 'FAILED' AND login_time >= datetime('now', '-1 hour') "
                "GROUP BY username HAVING fail_count >= 3"
            )
            
            for row in cursor.fetchall():
                user = row[0]
                count = row[1]
                
                if count >= 5:
                    alerts.append({
                        "type": "CRITICAL",
                        "title": f"Multiple Failed Logins: {user}",
                        "desc": f"{count} failed login attempts in the last hour."
                    })
                else:
                    alerts.append({
                        "type": "WARNING",
                        "title": f"Suspicious Logins: {user}",
                        "desc": f"{count} failed login attempts recently."
                    })
                    
            return alerts
        except Exception as e:
            print(f"Detect suspicious activity error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_security_overview_stats():
        """Get stats for the security dashboard overview cards."""
        conn = get_db_connection()
        if not conn:
            return {"active_sessions": 0, "failed_logins": 0, "frozen_accounts": 0}
            
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM active_sessions WHERE status = 'ACTIVE'")
            active = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM login_history WHERE status = 'FAILED'")
            failed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE account_status = 'FROZEN'")
            frozen = cursor.fetchone()[0]
            
            return {
                "active_sessions": active,
                "failed_logins": failed,
                "frozen_accounts": frozen
            }
        except Exception as e:
            print(f"Get security stats error: {e}")
            return {"active_sessions": 0, "failed_logins": 0, "frozen_accounts": 0}
        finally:
            conn.close()
