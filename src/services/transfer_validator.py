"""
Transfer Validator — Đăng Khoa Bank
Centralized validation for ALL transfer operations.
Prevents invalid, duplicate, and unsafe transfers before they reach the database.
"""

from datetime import datetime, timedelta
from src.database.database import get_db_connection


# ─── Transfer Limit Constants ────────────────────────────────────────────────

MIN_TRANSFER_AMOUNT = 10_000.0       # 10,000 VND minimum
MAX_TRANSFER_AMOUNT = 500_000_000.0  # 500M VND per-transaction max
DAILY_TRANSFER_LIMIT = 2_000_000_000.0  # 2B VND daily limit
DUPLICATE_WINDOW_SECONDS = 30        # Prevent duplicate transfers within 30s


class TransferValidator:
    """Validates all aspects of a transfer before execution."""

    @staticmethod
    def validate_transfer(sender_username: str, receiver_account: str,
                          amount: float, sender_balance: float,
                          sender_account_status: str = "ACTIVE") -> tuple[bool, str]:
        """
        Run ALL transfer validations in sequence.
        Returns (is_valid, error_message).
        """
        # 1. Validate account status
        valid, msg = TransferValidator.validate_account_status(sender_account_status)
        if not valid:
            return False, msg

        # 2. Validate amount
        valid, msg = TransferValidator.validate_amount(amount)
        if not valid:
            return False, msg

        # 3. Validate balance sufficiency
        valid, msg = TransferValidator.validate_balance(sender_balance, amount)
        if not valid:
            return False, msg

        # 4. Validate receiver exists
        valid, msg = TransferValidator.validate_receiver_exists(receiver_account)
        if not valid:
            return False, msg

        # 5. Prevent self-transfer
        valid, msg = TransferValidator.validate_self_transfer(sender_username, receiver_account)
        if not valid:
            return False, msg

        # 6. Check daily transfer limit
        valid, msg = TransferValidator.validate_daily_limit(sender_username, amount)
        if not valid:
            return False, msg

        # 7. Check duplicate transfer
        valid, msg = TransferValidator.validate_duplicate_transfer(
            sender_username, receiver_account, amount
        )
        if not valid:
            return False, msg

        return True, "Validation passed."

    @staticmethod
    def validate_amount(amount: float) -> tuple[bool, str]:
        """Validate the transfer amount is within allowed range."""
        if amount is None:
            return False, "Transfer amount is required."

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return False, "Invalid transfer amount."

        if amount <= 0:
            return False, "Transfer amount must be greater than zero."

        if amount < MIN_TRANSFER_AMOUNT:
            return False, f"Minimum transfer amount is {MIN_TRANSFER_AMOUNT:,.0f} VND."

        if amount > MAX_TRANSFER_AMOUNT:
            return False, f"Maximum transfer amount is {MAX_TRANSFER_AMOUNT:,.0f} VND per transaction."

        return True, "Valid amount."

    @staticmethod
    def validate_balance(balance: float, amount: float) -> tuple[bool, str]:
        """Ensure sender has sufficient balance. Balance must never go negative."""
        if balance is None or balance < 0:
            return False, "Invalid account balance."

        if balance < amount:
            return False, f"Insufficient balance. Available: {balance:,.0f} VND."

        return True, "Sufficient balance."

    @staticmethod
    def validate_receiver_exists(receiver_account: str) -> tuple[bool, str]:
        """Check if the receiver account exists in the system (for internal transfers)."""
        if not receiver_account or not receiver_account.strip():
            return False, "Receiver account number is required."

        conn = get_db_connection()
        if not conn:
            return False, "Database connection error."

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, account_status FROM users WHERE account_number = ? OR phone = ?",
                (receiver_account.strip(), receiver_account.strip())
            )
            row = cursor.fetchone()
            if not row:
                return False, "Account not found."

            receiver_status = row["account_status"] if row["account_status"] else "ACTIVE"
            if receiver_status in ("FROZEN", "SUSPENDED"):
                return False, "Receiver account is not available for transfers."

            return True, "Receiver found."
        except Exception as e:
            return False, f"Error verifying receiver: {e}"
        finally:
            conn.close()

    @staticmethod
    def validate_self_transfer(sender_username: str, receiver_account: str) -> tuple[bool, str]:
        """Prevent sending money to yourself."""
        conn = get_db_connection()
        if not conn:
            return False, "Database connection error."

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT account_number, phone FROM users WHERE username = ?",
                (sender_username,)
            )
            row = cursor.fetchone()
            if row:
                sender_acc = row["account_number"] or ""
                sender_phone = row["phone"] or ""
                receiver = receiver_account.strip()

                if receiver == sender_acc or receiver == sender_phone:
                    return False, "You cannot transfer to your own account."

            return True, "Not a self-transfer."
        except Exception as e:
            return False, f"Error checking self-transfer: {e}"
        finally:
            conn.close()

    @staticmethod
    def validate_account_status(account_status: str) -> tuple[bool, str]:
        """Check sender account is in a transferable state."""
        if account_status == "FROZEN":
            return False, "Your account is temporarily frozen. Transfers are disabled."
        if account_status == "SUSPENDED":
            return False, "Your account has been suspended. Please contact support."
        return True, "Account is active."

    @staticmethod
    def validate_daily_limit(sender_username: str, amount: float) -> tuple[bool, str]:
        """Check if the transfer would exceed the daily limit."""
        conn = get_db_connection()
        if not conn:
            return False, "Database connection error."

        try:
            cursor = conn.cursor()
            today_start = datetime.now().replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """SELECT COALESCE(SUM(amount), 0) as daily_total
                   FROM transactions
                   WHERE sender_username = ?
                     AND status = 'SUCCESS'
                     AND created_at >= ?""",
                (sender_username, today_start)
            )
            row = cursor.fetchone()
            daily_total = row["daily_total"] if row else 0.0

            if daily_total + amount > DAILY_TRANSFER_LIMIT:
                remaining = max(0, DAILY_TRANSFER_LIMIT - daily_total)
                return False, f"Daily transfer limit exceeded. Remaining today: {remaining:,.0f} VND."

            return True, "Within daily limit."
        except Exception as e:
            return False, f"Error checking daily limit: {e}"
        finally:
            conn.close()

    @staticmethod
    def validate_duplicate_transfer(sender_username: str, receiver_account: str,
                                    amount: float) -> tuple[bool, str]:
        """Prevent duplicate transfers within a short time window."""
        conn = get_db_connection()
        if not conn:
            return False, "Database connection error."

        try:
            cursor = conn.cursor()
            cutoff = (datetime.now() - timedelta(seconds=DUPLICATE_WINDOW_SECONDS)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """SELECT COUNT(*) as cnt
                   FROM transactions
                   WHERE sender_username = ?
                     AND receiver_account = ?
                     AND amount = ?
                     AND status = 'SUCCESS'
                     AND created_at >= ?""",
                (sender_username, receiver_account, amount, cutoff)
            )
            row = cursor.fetchone()
            if row and row["cnt"] > 0:
                return False, "Duplicate transfer detected. Please wait before sending again."

            return True, "No duplicate found."
        except Exception as e:
            return False, f"Error checking duplicate: {e}"
        finally:
            conn.close()
