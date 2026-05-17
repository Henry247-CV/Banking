from src.database.database import get_db_connection

class NotificationService:
    @staticmethod
    def create_notification(username, title, message, n_type="INFO"):
        """Creates a new notification for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO notifications (username, title, message, type) VALUES (?, ?, ?, ?)",
                (username, title, message, n_type)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Notification error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_notifications(username):
        """Retrieves all notifications for a user, sorted by newest first."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, message, type, is_read, created_at FROM notifications WHERE username = ? ORDER BY created_at DESC",
            (username,)
        )
        notifications = cursor.fetchall()
        conn.close()
        return notifications

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
