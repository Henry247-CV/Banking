"""
Dịch vụ Giao dịch — Đăng Khoa Bank
Động cơ giao dịch cốt lõi với các giao dịch SQLite nguyên tử, bảo vệ khôi phục,
và ghi nhật ký kiểm tra đầy đủ.
"""

import os
import traceback
from datetime import datetime
from pathlib import Path

from src.database.database import get_db_connection
from src.models.transaction_model import Transaction, TransactionStatus, TransactionType
from src.services.wallet_service import WalletService
from src.services.transfer_validator import TransferValidator
from src.services.notification_service import NotificationService
from src.services.tier_service import TierService
from src.core.exception_handler import GlobalExceptionHandler


class TransactionService:
    """Thực hiện, ghi nhật ký và quản lý các giao dịch ngân hàng."""

    DEBUG_MODE = True # Đặt thành False cho môi trường thực tế (production)

    # ─── Luồng Chuyển tiền Cốt lõi ───────────────────────────────────────────────

    @staticmethod
    def execute_transfer(sender_username: str, receiver_bank: str,
                         receiver_account: str, amount: float,
                         note: str = "", transaction_type: str = TransactionType.TRANSFER) -> tuple[bool, str, Transaction | None]:
        """
        Thực hiện chuyển tiền đầy đủ với tính nguyên tử và tính nhất quán nghiêm ngặt.
        """
        # 1. Các xác thực cơ bản
        if amount <= 0:
            return False, "Invalid transfer amount.", None

        # Giải quyết số điện thoại hoặc tài khoản thành tên người dùng người nhận (nếu nội bộ)
        is_internal = receiver_bank in ("Đăng Khoa Bank", "DKB")
        receiver_username = None
        
        if is_internal:
            from src.services.account_lookup_service import AccountLookupService
            receiver_user = AccountLookupService.validate_receiver(receiver_account)
            
            if not receiver_user:
                return False, f"Receiver account '{receiver_account}' not found in Đăng Khoa Bank.", None
            
            receiver_username = receiver_user['username']
            if receiver_username == sender_username:
                return False, "You cannot transfer to your own account.", None

        # Giữ khóa ví tạm thời
        if not WalletService.lock_wallet_temporarily(sender_username):
            return False, "Wallet is temporarily locked. Please try again.", None

        conn = get_db_connection()
        if not conn:
            WalletService.unlock_wallet(sender_username)
            return False, "Database connection error.", None

        txn = Transaction(
            sender_username=sender_username,
            receiver_bank=receiver_bank,
            receiver_account=receiver_account,
            amount=amount,
            note=note,
            transaction_type=transaction_type,
            status=TransactionStatus.PENDING,
        )

        try:
            cursor = conn.cursor()
            
            if TransactionService.DEBUG_MODE:
                print(f"[DEBUG] Starting transfer: {amount} VND from {sender_username} to {receiver_account}")

            # ─── BẮT ĐẦU GIAO DỊCH ───
            cursor.execute("BEGIN TRANSACTION")

            # 2. Lấy Số dư Người gửi
            cursor.execute(
                "SELECT balance, account_status FROM users WHERE username = ?",
                (sender_username,),
            )
            sender_row = cursor.fetchone()
            if not sender_row:
                raise Exception("Sender account not found.")

            sender_balance = float(sender_row["balance"])
            sender_status = sender_row["account_status"] or "ACTIVE"

            if TransactionService.DEBUG_MODE:
                print(f"[DEBUG] Sender validated. Current balance: {sender_balance}")

            # 3. Xác thực Cuối cùng
            valid, msg = TransferValidator.validate_transfer(
                sender_username=sender_username,
                receiver_account=receiver_account,
                amount=amount,
                sender_balance=sender_balance,
                sender_account_status=sender_status,
            )
            if not valid:
                raise Exception(msg)

            if TransactionService.DEBUG_MODE:
                print("[DEBUG] Transfer validation passed.")

            # 4. Ghi nợ Người gửi
            new_sender_balance = sender_balance - amount
            cursor.execute(
                "UPDATE users SET balance = ? WHERE username = ?",
                (new_sender_balance, sender_username),
            )
            if TransactionService.DEBUG_MODE:
                print(f"[DEBUG] Sender debited. New balance: {new_sender_balance}")

            # 5. Ghi có Người nhận (Nội bộ)
            if is_internal and receiver_username:
                cursor.execute(
                    "SELECT balance FROM users WHERE username = ?",
                    (receiver_username,),
                )
                receiver_row = cursor.fetchone()
                if not receiver_row:
                    raise Exception("Internal receiver disappeared.")
                
                new_receiver_balance = float(receiver_row["balance"]) + amount
                cursor.execute(
                    "UPDATE users SET balance = ? WHERE username = ?",
                    (new_receiver_balance, receiver_username),
                )
                if TransactionService.DEBUG_MODE:
                    print(f"[DEBUG] Receiver credited. New balance: {new_receiver_balance}")

            # 6. Ghi nhật ký Giao dịch
            txn.status = TransactionStatus.SUCCESS
            TransactionService._save_transaction_log(txn, conn)

            # ─── CAM KẾT (COMMIT) ───
            conn.commit()
            if TransactionService.DEBUG_MODE:
                print("[DEBUG] Database transaction committed successfully.")
            
            # 7. Xác minh Sau khi Cam kết
            cursor.execute("SELECT balance FROM users WHERE username = ?", (sender_username,))
            verify_sender = cursor.fetchone()
            if is_internal and receiver_username:
                cursor.execute("SELECT balance FROM users WHERE username = ?", (receiver_username,))
                verify_receiver = cursor.fetchone()
                
                print(f"[DEBUG] Transfer Successful: {amount} VND")
                print(f"[DEBUG] Sender: {sender_username} | New Balance: {verify_sender['balance']}")
                print(f"[DEBUG] Receiver: {receiver_username} | New Balance: {verify_receiver['balance']}")
            
            # 8. Tác dụng phụ sau cam kết (Thông báo)
            try:
                TierService.update_user_tier(sender_username, new_sender_balance)
                NotificationService.create_notification(
                    sender_username,
                    "Transfer Successful",
                    f"You transferred {amount:,.0f} VND to {receiver_bank} — {receiver_account}.",
                    "TRANSFER",
                )
                
                if is_internal and receiver_username:
                    NotificationService.create_notification(
                        receiver_username,
                        "Money Received",
                        f"You received {amount:,.0f} VND from {sender_username}.",
                        "TRANSFER",
                    )
                    TierService.update_user_tier(receiver_username, new_receiver_balance)
            except Exception as ne:
                print(f"[TransactionService] Side effects error: {ne}")

            return True, "Transfer completed successfully.", txn

        except Exception as e:
            # ─── KHÔI PHỤC (ROLLBACK) ───
            try:
                conn.rollback()
            except Exception:
                pass

            txn.status = TransactionStatus.FAILED
            # Tùy chọn: Ghi nhật ký cả lỗi thất bại
            try:
                TransactionService.save_transaction_log(txn)
            except Exception:
                pass

            return False, f"Transfer failed: {str(e)}", None
        finally:
            try:
                conn.close()
            except Exception:
                pass
            WalletService.unlock_wallet(sender_username)

    # ─── Nhật ký Giao dịch ──────────────────────────────────────────────────

    @staticmethod
    def _save_transaction_log(txn: Transaction, conn) -> bool:
        """Lưu hồ sơ giao dịch bằng kết nối hiện có (bên trong một khối giao dịch)."""
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO transactions
                   (transaction_id, sender_username, receiver_bank, receiver_account,
                    amount, note, status, transaction_type, flagged, risk_level, review_status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    txn.transaction_id,
                    txn.sender_username,
                    txn.receiver_bank,
                    txn.receiver_account,
                    txn.amount,
                    txn.note,
                    txn.status,
                    txn.transaction_type,
                    txn.flagged,
                    txn.risk_level,
                    txn.review_status,
                    txn.created_at,
                ),
            )
            return True
        except Exception as e:
            print(f"[TransactionService] Log error: {e}")
            return False

    @staticmethod
    def save_transaction_log(txn: Transaction) -> bool:
        """Lưu hồ sơ giao dịch bằng kết nối độc lập (ghi nhật ký sau khi khôi phục)."""
        conn = get_db_connection()
        if not conn:
            return False
        try:
            result = TransactionService._save_transaction_log(txn, conn)
            conn.commit()
            return result
        except Exception:
            return False
        finally:
            conn.close()

    # ─── Giao dịch Tiết kiệm ─────────────────────────────────────────────

    @staticmethod
    def create_savings_transaction(username: str, savings_id: str, amount: float, 
                                 txn_type: str, status: str = TransactionStatus.SUCCESS) -> bool:
        """Tạo một hồ sơ trong lịch sử giao dịch chính cho một hoạt động tiết kiệm."""
        conn = get_db_connection()
        if not conn:
            return False
        try:
            from src.models.transaction_model import Transaction
            txn = Transaction(
                sender_username=username,
                receiver_bank="Đăng Khoa Bank",
                receiver_account=f"SAVINGS-{savings_id}",
                amount=amount,
                note=f"{txn_type} for savings plan {savings_id}",
                transaction_type=f"SAVINGS_{txn_type}",
                status=status
            )
            return TransactionService.save_transaction_log(txn)
        except Exception as e:
            print(f"TransactionService.create_savings_transaction error: {e}")
            return False

    @staticmethod
    def create_savings_history(savings_id: str, amount: float, txn_type: str, conn=None) -> bool:
        """Trình hỗ trợ nội bộ để ghi một hồ sơ vào bảng savings_transactions cụ thể."""
        own_conn = conn is None
        if own_conn:
            conn = get_db_connection()
            if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO savings_transactions (savings_id, amount, transaction_type) VALUES (?, ?, ?)",
                (savings_id, amount, txn_type)
            )
            if own_conn: conn.commit()
            return True
        except Exception as e:
            if own_conn: conn.rollback()
            print(f"TransactionService.create_savings_history error: {e}")
            return False
        finally:
            if own_conn: conn.close()

    @staticmethod
    def create_admin_savings_log(admin_username: str, action: str, target_user: str, details: str, conn=None) -> bool:
        """Trình hỗ trợ nội bộ để ghi nhật ký các hành động tiết kiệm cho việc kiểm tra của quản trị viên."""
        own_conn = conn is None
        if own_conn:
            conn = get_db_connection()
            if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admin_logs (admin_username, action, target, created_at) VALUES (?, ?, ?, ?)",
                (admin_username, action, f"User: {target_user} | {details}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            if own_conn: conn.commit()
            return True
        except Exception as e:
            if own_conn: conn.rollback()
            print(f"TransactionService.create_admin_savings_log error: {e}")
            return False
        finally:
            if own_conn: conn.close()

    # ─── Khôi phục (thủ công) ────────────────────────────────────────────────

    @staticmethod
    def rollback_transaction(transaction_id: str) -> tuple[bool, str]:
        """
        Đánh dấu một giao dịch là ROLLED_BACK (ĐÃ KHÔI PHỤC). Điều này KHÔNG đảo ngược số dư;
        nó là một bản cập nhật trạng thái cho mục đích kiểm tra. Việc đảo ngược số dư nên
        được xử lý bằng một giao dịch bù mới.
        """
        conn = get_db_connection()
        if not conn:
            return False, "Database connection error."
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transactions SET status = ? WHERE transaction_id = ?",
                (TransactionStatus.ROLLED_BACK, transaction_id),
            )
            conn.commit()
            return True, "Transaction marked as rolled back."
        except Exception as e:
            conn.rollback()
            return False, f"Rollback update error: {e}"
        finally:
            conn.close()

    # ─── Truy vấn Lịch sử ──────────────────────────────────────────────────

    @staticmethod
    def get_transaction_history(username: str, limit: int = 50) -> list:
        """Lấy tất cả các giao dịch của một người dùng (đã gửi hoặc đã nhận), được sắp xếp theo mới nhất."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, transaction_id, sender_username, receiver_bank,
                          receiver_account, amount, note, status,
                          transaction_type, created_at
                   FROM transactions
                   WHERE sender_username = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (username, limit),
            )
            return cursor.fetchall()
        except Exception as e:
            GlobalExceptionHandler.log_error(f"TransactionService.get_transaction_history error for {username}:\n{traceback.format_exc()}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_user_transactions(username: str) -> list:
        """
        Phương thức tương thích ngược trả về các giao dịch theo cùng định dạng
        tuple như TransferService.get_user_transactions() cũ.
        """
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT created_at, receiver_bank, receiver_account, amount, status
                   FROM transactions
                   WHERE sender_username = ?
                   ORDER BY created_at DESC""",
                (username,),
            )
            return cursor.fetchall()
        except Exception as e:
            GlobalExceptionHandler.log_error(f"TransactionService.get_user_transactions error for {username}:\n{traceback.format_exc()}")
            return []
        finally:
            conn.close()

    # ─── Truy vấn Lịch sử ──────────────────────────────────────────────────
