import sys
import os

# Allow absolute imports from 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.database import get_db_connection
from src.models.admin_action_model import AdminAction

class AdminAuditService:
    """Service for tracking and logging all administrative actions."""

    @staticmethod
    def log_action(admin_username, action_type, target_username, details=""):
        """Lưu một hành động admin vào nhật ký kiểm toán."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # Ensure the admin_logs table can handle the details if we were to add a column,
            # but for now we'll stick to the existing schema or concatenate.
            # Existing schema: admin_username, action, target, created_at
            action_with_details = f"{action_type}: {details}" if details else action_type
            
            cursor.execute(
                "INSERT INTO admin_logs (admin_username, action, target) VALUES (?, ?, ?)",
                (admin_username, action_with_details, target_username)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Audit Log Error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_audit_logs(limit=100):
        """Retrieves recent audit logs."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
