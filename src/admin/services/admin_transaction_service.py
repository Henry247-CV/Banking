"""Admin Transaction Service — Database operations for transaction monitoring.

Provides search, filtering, risk calculation, flagging, and status management
for the admin transaction control center.
"""

from src.database.database import get_db_connection
from src.services.notification_service import NotificationService
from src.admin.services.security_service import SecurityService

class AdminTransactionService:
    """Service layer for admin transaction management."""

    VALID_REVIEW_STATUSES = ("COMPLETED", "PENDING", "BLOCKED", "REVIEWING")
    VALID_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    # Simple rule-based thresholds (VND)
    HIGH_RISK_THRESHOLD = 50_000_000
    CRITICAL_RISK_THRESHOLD = 100_000_000
    RAPID_TRANSFER_COUNT = 5  # transfers within same day = MEDIUM

    @staticmethod
    def get_all_transactions(limit=200):
        """Retrieve all transactions with full details, newest first."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, sender_username, receiver_bank, receiver_account, "
                "amount, note, status, created_at, flagged, risk_level, review_status "
                "FROM transactions ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"AdminTransactionService.get_all_transactions error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def search_transactions(query="", status_filter="All", risk_filter="All",
                            date_filter="All"):
        """Search and filter transactions with combined criteria.

        Args:
            query: Search text (sender, receiver, transaction ID).
            status_filter: Filter by review_status.
            risk_filter: Filter by risk_level.
            date_filter: 'All', 'Today', 'Last 7 Days', 'Last 30 Days'.
        """
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()

            sql = (
                "SELECT id, sender_username, receiver_bank, receiver_account, "
                "amount, note, status, created_at, flagged, risk_level, review_status "
                "FROM transactions WHERE 1=1"
            )
            params = []

            if query.strip():
                sql += (
                    " AND (sender_username LIKE ? OR receiver_account LIKE ? "
                    "OR CAST(id AS TEXT) LIKE ?)"
                )
                like = f"%{query.strip()}%"
                params.extend([like, like, like])

            if status_filter and status_filter != "All":
                sql += " AND review_status = ?"
                params.append(status_filter.upper())

            if risk_filter and risk_filter != "All":
                sql += " AND risk_level = ?"
                params.append(risk_filter.upper())

            if date_filter == "Today":
                sql += " AND DATE(created_at) = DATE('now')"
            elif date_filter == "Last 7 Days":
                sql += " AND created_at >= datetime('now', '-7 days')"
            elif date_filter == "Last 30 Days":
                sql += " AND created_at >= datetime('now', '-30 days')"

            sql += " ORDER BY created_at DESC LIMIT 200"
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"AdminTransactionService.search_transactions error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_transaction_by_id(txn_id):
        """Get a single transaction's full details."""
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, sender_username, receiver_bank, receiver_account, "
                "amount, note, status, created_at, flagged, risk_level, review_status "
                "FROM transactions WHERE id = ?",
                (txn_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"AdminTransactionService.get_transaction_by_id error: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def flag_transaction(txn_id, flagged=True):
        """Flag or unflag a transaction."""
        conn = get_db_connection()
        if not conn:
            return False, "Database connection failed."
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transactions SET flagged = ? WHERE id = ?",
                (1 if flagged else 0, txn_id)
            )
            conn.commit()
            
            # Log admin action
            action_type = "FLAG_TRANSACTION" if flagged else "UNFLAG_TRANSACTION"
            SecurityService.log_admin_action("admin", action_type, f"TxID:{txn_id}")
            
            action = "flagged" if flagged else "unflagged"
            return True, f"Transaction #{txn_id} {action}."
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def update_review_status(txn_id, new_status):
        """Update a transaction's review status."""
        new_status = new_status.upper()
        if new_status not in AdminTransactionService.VALID_REVIEW_STATUSES:
            return False, f"Invalid status: {new_status}"

        conn = get_db_connection()
        if not conn:
            return False, "Database connection failed."
        try:
            cursor = conn.cursor()

            # Verify transaction exists
            cursor.execute("SELECT review_status FROM transactions WHERE id = ?", (txn_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Transaction not found."

            old_status = row[0] or "COMPLETED"
            if old_status == new_status:
                return False, f"Transaction is already {new_status}."

            cursor.execute(
                "UPDATE transactions SET review_status = ? WHERE id = ?",
                (new_status, txn_id)
            )
            conn.commit()

            # Log admin action
            SecurityService.log_admin_action("admin", f"UPDATE_REVIEW_{new_status}", f"TxID:{txn_id}")

            # If blocking, also notify the sender
            if new_status == "BLOCKED":
                cursor.execute(
                    "SELECT sender_username, amount FROM transactions WHERE id = ?",
                    (txn_id,)
                )
                txn_row = cursor.fetchone()
                if txn_row:
                    NotificationService.create_notification(
                        str(txn_row[0]),
                        "Transaction Blocked",
                        f"Your transaction #{txn_id} has been blocked by admin review.",
                        "SECURITY"
                    )

            return True, f"Status updated: {old_status} → {new_status}"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def update_risk_level(txn_id, risk_level):
        """Manually update a transaction's risk level."""
        risk_level = risk_level.upper()
        if risk_level not in AdminTransactionService.VALID_RISK_LEVELS:
            return False, f"Invalid risk level: {risk_level}"

        conn = get_db_connection()
        if not conn:
            return False, "Database connection failed."
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transactions SET risk_level = ? WHERE id = ?",
                (risk_level, txn_id)
            )
            conn.commit()
            
            # Log admin action
            SecurityService.log_admin_action("admin", "UPDATE_RISK_LEVEL", f"TxID:{txn_id}, Risk:{risk_level}")
            
            return True, f"Risk level set to {risk_level}."
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def calculate_risk_level(amount, sender_username=None):
        """Calculate risk level based on simple rules.

        Rules:
        - >= 100M VND → CRITICAL
        - >= 50M VND → HIGH
        - 5+ transfers same day by same sender → MEDIUM
        - Otherwise → LOW
        """
        if amount >= AdminTransactionService.CRITICAL_RISK_THRESHOLD:
            return "CRITICAL"
        if amount >= AdminTransactionService.HIGH_RISK_THRESHOLD:
            return "HIGH"

        # Check rapid transfers
        if sender_username:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    from datetime import datetime
                    today_start = datetime.now().replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "SELECT COUNT(*) FROM transactions "
                        "WHERE sender_username = ? AND created_at >= ?",
                        (sender_username, today_start)
                    )
                    count = cursor.fetchone()[0]
                    if count >= AdminTransactionService.RAPID_TRANSFER_COUNT:
                        return "MEDIUM"
                except Exception:
                    pass
                finally:
                    conn.close()

        return "LOW"

    @staticmethod
    def auto_assess_transaction(txn_id):
        """Auto-assess risk for an existing transaction and update DB."""
        txn = AdminTransactionService.get_transaction_by_id(txn_id)
        if not txn:
            return

        amount = abs(float(txn.get("amount", 0)))
        sender = txn.get("sender_username", "")
        risk = AdminTransactionService.calculate_risk_level(amount, sender)

        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            flagged = 1 if risk in ("HIGH", "CRITICAL") else 0
            cursor.execute(
                "UPDATE transactions SET risk_level = ?, flagged = ? WHERE id = ?",
                (risk, flagged, txn_id)
            )
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

    @staticmethod
    def get_flagged_count():
        """Get count of flagged transactions."""
        conn = get_db_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE flagged = 1")
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_critical_count():
        """Get count of critical risk transactions."""
        conn = get_db_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE risk_level IN ('HIGH', 'CRITICAL')"
            )
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()
