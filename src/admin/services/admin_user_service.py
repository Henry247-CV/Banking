"""Admin User Service — Safe, modular database operations for admin user management.

Provides CRUD operations for admin to manage users: search, filter,
update account status (ACTIVE/FROZEN/SUSPENDED), and manage tiers.
"""

from src.database.database import get_db_connection
from src.services.notification_service import NotificationService
from datetime import datetime


class AdminUserService:
    """Service layer for admin user management operations."""

    # Valid account statuses
    VALID_STATUSES = ("ACTIVE", "FROZEN", "SUSPENDED")

    # Valid customer tiers
    VALID_TIERS = ("STANDARD", "GOLD", "DIAMOND")

    # Tier hierarchy for upgrade/downgrade logic
    TIER_ORDER = ["STANDARD", "GOLD", "DIAMOND"]

    @staticmethod
    def get_all_users():
        """Retrieve all users ordered by creation date (newest first).
        
        Returns:
            list: List of sqlite3.Row objects, or empty list on error.
        """
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, full_name, phone, account_number, "
                "customer_tier, balance, account_status, last_login, created_at "
                "FROM users ORDER BY created_at DESC"
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"AdminUserService.get_all_users error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def search_users(query="", status_filter="All", tier_filter="All"):
        """Search and filter users with combined criteria.
        
        Args:
            query: Search text (matches username, phone, account_number).
            status_filter: Filter by account_status ('All', 'ACTIVE', 'FROZEN', 'SUSPENDED').
            tier_filter: Filter by customer_tier ('All', 'STANDARD', 'GOLD', 'DIAMOND').
        
        Returns:
            list: Filtered list of user rows.
        """
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            
            sql = (
                "SELECT id, username, full_name, phone, account_number, "
                "customer_tier, balance, account_status, last_login, created_at "
                "FROM users WHERE 1=1"
            )
            params = []

            # Search filter
            if query.strip():
                sql += (
                    " AND (username LIKE ? OR phone LIKE ? OR account_number LIKE ?)"
                )
                like_query = f"%{query.strip()}%"
                params.extend([like_query, like_query, like_query])

            # Status filter
            if status_filter and status_filter != "All":
                sql += " AND account_status = ?"
                params.append(status_filter.upper())

            # Tier filter
            if tier_filter and tier_filter != "All":
                sql += " AND customer_tier = ?"
                params.append(tier_filter.upper())

            sql += " ORDER BY created_at DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"AdminUserService.search_users error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_user_by_username(username):
        """Get a single user's full details by username.
        
        Returns:
            dict or None: User data as dict, or None if not found.
        """
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, full_name, phone, cccd, email, "
                "account_number, customer_tier, balance, account_status, "
                "last_login, created_at "
                "FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"AdminUserService.get_user_by_username error: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update_account_status(username, new_status):
        """Update a user's account status (ACTIVE/FROZEN/SUSPENDED).
        
        Safety checks:
        - Cannot modify admin account
        - Validates status is in VALID_STATUSES
        - Creates notification for user
        
        Args:
            username: Target username.
            new_status: New status string.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not username or not new_status:
            return False, "Invalid parameters."

        # Safety: prevent admin self-modification
        if username.lower() == "admin":
            return False, "Cannot modify admin account status."

        new_status = new_status.upper()
        if new_status not in AdminUserService.VALID_STATUSES:
            return False, f"Invalid status: {new_status}"

        conn = get_db_connection()
        if not conn:
            return False, "Database connection failed."
        try:
            cursor = conn.cursor()
            
            # Verify user exists
            cursor.execute(
                "SELECT account_status FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if not row:
                return False, "User not found."

            old_status = row[0] or "ACTIVE"
            if old_status == new_status:
                return False, f"Account is already {new_status}."

            cursor.execute(
                "UPDATE users SET account_status = ? WHERE username = ?",
                (new_status, username)
            )
            conn.commit()

            # Create notification for user
            status_messages = {
                "ACTIVE": "Your account has been reactivated. All services are now available.",
                "FROZEN": "Your account has been temporarily frozen. Transfers are disabled.",
                "SUSPENDED": "Your account has been suspended. Please contact support.",
            }
            NotificationService.create_notification(
                username,
                f"Account Status: {new_status}",
                status_messages.get(new_status, "Your account status has been updated."),
                "SECURITY"
            )

            return True, f"Account status updated to {new_status}."
        except Exception as e:
            print(f"AdminUserService.update_account_status error: {e}")
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def update_user_tier(username, new_tier):
        """Update a user's customer tier (STANDARD/GOLD/DIAMOND).
        
        Safety checks:
        - Cannot modify admin account
        - Validates tier is in VALID_TIERS
        - Creates notification for user
        
        Args:
            username: Target username.
            new_tier: New tier string.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not username or not new_tier:
            return False, "Invalid parameters."

        if username.lower() == "admin":
            return False, "Cannot modify admin account tier."

        new_tier = new_tier.upper()
        if new_tier not in AdminUserService.VALID_TIERS:
            return False, f"Invalid tier: {new_tier}"

        conn = get_db_connection()
        if not conn:
            return False, "Database connection failed."
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT customer_tier FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if not row:
                return False, "User not found."

            old_tier = row[0] or "STANDARD"
            if old_tier == new_tier:
                return False, f"User is already {new_tier}."

            cursor.execute(
                "UPDATE users SET customer_tier = ? WHERE username = ?",
                (new_tier, username)
            )
            conn.commit()

            # Determine direction
            old_idx = AdminUserService.TIER_ORDER.index(old_tier) if old_tier in AdminUserService.TIER_ORDER else 0
            new_idx = AdminUserService.TIER_ORDER.index(new_tier)
            direction = "upgraded" if new_idx > old_idx else "downgraded"

            NotificationService.create_notification(
                username,
                f"Tier {direction.title()}",
                f"Your membership has been {direction} from {old_tier} to {new_tier}.",
                "SUCCESS" if direction == "upgraded" else "WARNING"
            )

            return True, f"Tier updated: {old_tier} → {new_tier}"
        except Exception as e:
            print(f"AdminUserService.update_user_tier error: {e}")
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_user_count():
        """Get total number of users."""
        conn = get_db_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()
