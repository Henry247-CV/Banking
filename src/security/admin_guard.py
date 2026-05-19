from src.database.database import get_db_connection

class AdminGuard:
    """Security layer to protect admin actions."""

    @staticmethod
    def is_admin(username):
        """Verifies if the user has administrative privileges."""
        # In this system, 'admin' is the reserved username for the administrator
        return username == "admin"

    @staticmethod
    def validate_session(username, session_token):
        """Validates if the admin session is active and legitimate."""
        if not AdminGuard.is_admin(username):
            return False
            
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM active_sessions WHERE username = ? AND session_token = ? AND status = 'ACTIVE'",
                (username, session_token)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def can_perform_action(admin_username, target_username):
        """Ngăn chặn quản trị viên thực hiện các hành động quan trọng trên chính họ."""
        if admin_username == target_username:
            return False, "You cannot perform this action on your own account."
        return True, ""
