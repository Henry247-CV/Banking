from src.database.database import get_db_connection
from datetime import datetime

class AdminNotificationService:
    @staticmethod
    def create_notification(title, message, n_type="INFO", priority="LOW", target="ALL_USERS", created_by="admin"):
        """Creates a new administrative notification/broadcast."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO notifications (title, message, type, priority, target, created_by) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (title, message, n_type, priority, target, created_by)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Admin Notification error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_notification_history(limit=50):
        """Retrieves history of administrative notifications."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, title, type, priority, target, created_at, created_by 
                   FROM notifications 
                   WHERE created_by != 'SYSTEM' 
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting notification history: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_recent_announcements(limit=5):
        """Retrieves most recent global announcements for dashboard display."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT title, type, priority, created_at, message 
                   FROM notifications 
                   WHERE target = 'ALL_USERS' OR target LIKE '%_USERS'
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting recent announcements: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def delete_notification(notif_id):
        """Permanently removes a notification."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications WHERE id = ?", (notif_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting notification: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_active_maintenance_alerts():
        """Returns active maintenance alerts (priority HIGH/CRITICAL)."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Simplified: any MAINTENANCE type notif created in last 24h
            cursor.execute(
                """SELECT title, message, priority FROM notifications 
                   WHERE type = 'MAINTENANCE' AND created_at > datetime('now', '-1 day')
                   ORDER BY created_at DESC"""
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting maintenance alerts: {e}")
            return []
        finally:
            conn.close()
