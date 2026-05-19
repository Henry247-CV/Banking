"""
Wallet Service — Đăng Khoa Bank
Handles all wallet-related operations: balance queries, updates, summaries.
All balance mutations go through this service layer.
"""

import threading
import traceback
from datetime import datetime
from src.database.database import get_db_connection
from src.models.wallet_model import Wallet, DEFAULT_CURRENCY


# ─── Wallet Lock Manager ─────────────────────────────────────────────────────
# Prevents concurrent modifications to the same wallet during a transfer.

_wallet_locks: dict[str, threading.Lock] = {}
_lock_manager = threading.Lock()


def _get_wallet_lock(username: str) -> threading.Lock:
    """Get or create a per-user lock to serialize wallet mutations."""
    with _lock_manager:
        if username not in _wallet_locks:
            _wallet_locks[username] = threading.Lock()
        return _wallet_locks[username]


from src.core.exception_handler import GlobalExceptionHandler

class WalletService:
    """Service layer for wallet / balance operations."""

    @staticmethod
    def get_balance(username: str) -> float:
        """Retrieve the current balance for a user."""
        conn = get_db_connection()
        if not conn:
            return 0.0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return float(row["balance"]) if row else 0.0
        except Exception as e:
            GlobalExceptionHandler.log_error(f"WalletService.get_balance error for {username}:\n{traceback.format_exc()}")
            return 0.0
        finally:
            conn.close()

    @staticmethod
    def validate_balance(username: str, amount: float) -> tuple[bool, str]:
        """Check if the user has sufficient balance for a withdrawal."""
        balance = WalletService.get_balance(username)
        if balance < amount:
            return False, f"Insufficient balance. Available: {balance:,.0f} VND."
        return True, "Sufficient balance."

    @staticmethod
    def update_balance(username: str, new_balance: float, conn=None) -> bool:
        """
        Update a user's balance.  Accepts an external connection for
        transactional use (the caller is responsible for commit/rollback).
        If no conn is passed, a standalone connection is used.
        """
        own_conn = conn is None
        if own_conn:
            conn = get_db_connection()
            if not conn:
                return False

        try:
            cursor = conn.cursor()
            # Check status before updating
            cursor.execute("SELECT account_status FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and row["account_status"] in ("FROZEN", "SUSPENDED"):
                print(f"[WalletService] Balance update blocked: Account {username} is {row['account_status']}")
                return False

            cursor.execute(
                "UPDATE users SET balance = ? WHERE username = ?",
                (new_balance, username),
            )
            if own_conn:
                conn.commit()
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            GlobalExceptionHandler.log_error(f"WalletService.update_balance error for {username}:\n{traceback.format_exc()}")
            return False
        finally:
            if own_conn:
                conn.close()

    @staticmethod
    def get_wallet(username: str) -> Wallet | None:
        """Retrieve the full wallet object for a user."""
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return Wallet.from_db_row(dict(row))
            return None
        except Exception as e:
            GlobalExceptionHandler.log_error(f"WalletService.get_wallet error for {username}:\n{traceback.format_exc()}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_wallet_summary(username: str) -> dict:
        """
        Get a concise wallet summary for UI display.
        Returns balance, currency, tier, and account status.
        """
        wallet = WalletService.get_wallet(username)
        if not wallet:
            return {
                "balance": 0.0,
                "currency": DEFAULT_CURRENCY,
                "customer_tier": "STANDARD",
                "account_status": "UNKNOWN",
                "account_number": "",
            }
        return {
            "balance": wallet.balance,
            "currency": wallet.currency,
            "customer_tier": wallet.customer_tier,
            "account_status": wallet.account_status,
            "account_number": wallet.account_number,
        }

    @staticmethod
    def lock_wallet_temporarily(username: str) -> bool:
        """
        Acquire a per-user lock to prevent concurrent wallet mutations.
        Returns True if the lock was acquired.  The caller MUST call
        unlock_wallet() when done.
        """
        lock = _get_wallet_lock(username)
        acquired = lock.acquire(timeout=10)
        return acquired

    @staticmethod
    def unlock_wallet(username: str) -> None:
        """Release a previously acquired wallet lock."""
        lock = _get_wallet_lock(username)
        try:
            lock.release()
        except RuntimeError:
            pass  # Already released — safe to ignore

    @staticmethod
    def ensure_wallet_exists(username: str) -> bool:
        """
        Ensures a user has a wallet (balance record).
        In this system, wallets are integrated into the users table.
        This checks if the user row exists and has a balance initialized.
        """
        conn = get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if not row:
                # User doesn't exist, we can't create a wallet without user info
                return False
            
            if row["balance"] is None:
                cursor.execute(
                    "UPDATE users SET balance = 10000000.0 WHERE username = ?",
                    (username,)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"[WalletService] ensure_wallet_exists error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def credit_receiver(receiver_account: str, amount: float, conn=None) -> bool:
        """
        Credit (add) an amount to a receiver's wallet.
        Uses the provided connection for transactional safety.
        """
        own_conn = conn is None
        if own_conn:
            conn = get_db_connection()
            if not conn:
                return False

        try:
            cursor = conn.cursor()
            # Lookup receiver by account_number or phone
            cursor.execute(
                "SELECT username, balance, account_status FROM users WHERE account_number = ? OR phone = ?",
                (receiver_account, receiver_account),
            )
            row = cursor.fetchone()
            if not row:
                return False
            
            if row["account_status"] in ("FROZEN", "SUSPENDED"):
                print(f"[WalletService] Credit blocked: Receiver {row['username']} is {row['account_status']}")
                return False

            new_balance = float(row["balance"]) + amount
            cursor.execute(
                "UPDATE users SET balance = ? WHERE username = ?",
                (new_balance, row["username"]),
            )
            if own_conn:
                conn.commit()
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"[WalletService] Credit receiver error: {e}")
            return False
        finally:
            if own_conn:
                conn.close()
