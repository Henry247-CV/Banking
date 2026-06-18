from src.database.database import get_db_connection

class NotificationService:
    @staticmethod
    def create_notification(username, title, message, n_type="INFO", target="PERSONAL"):
        """Creates a new notification for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            from datetime import datetime
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO notifications (username, title, message, type, target, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (username, title, message, n_type, target, created_at)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Notification error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_notifications(username, tier="STANDARD"):
        """Retrieves all notifications for a user (personal + broadcast), sorted by newest first."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        target_tier = f"{tier}_USERS"
        
        cursor.execute(
            """
            SELECT id, title, message, type, is_read, created_at, priority 
            FROM notifications 
            WHERE username = ? 
               OR target = 'ALL_USERS' 
               OR target = ?
            ORDER BY created_at DESC
            """,
            (username, target_tier)
        )
        notifications = cursor.fetchall()
        conn.close()
        return notifications

    @staticmethod
    def get_active_maintenance_alerts():
        """Returns active maintenance alerts (priority HIGH/CRITICAL) for the user app."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT title, message, priority FROM notifications 
                   WHERE type = 'MAINTENANCE' AND created_at > datetime('now', '-1 day')
                   ORDER BY created_at DESC LIMIT 1"""
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting maintenance alerts: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def mark_all_as_read(username):
        """Marks all unread notifications as read for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE username = ? AND is_read = 0", (username,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking as read: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def clear_notifications(username):
        """Deletes all notifications for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM notifications WHERE username = ?", (username,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing notifications: {e}")
            return False
        finally:
            conn.close()
