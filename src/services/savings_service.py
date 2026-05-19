"""
Dịch vụ Tiết kiệm — Đăng Khoa Bank
Xử lý tất cả logic kinh doanh liên quan đến tiết kiệm, các hoạt động cơ sở dữ liệu và đồng bộ hóa ví.
"""

import traceback
from datetime import datetime, timedelta
from src.database.database import get_db_connection
from src.models.savings_model import SavingsAccount, SavingsType, SavingsStatus
from src.models.transaction_model import Transaction, TransactionStatus, TransactionType
from src.services.wallet_service import WalletService
from src.services.transaction_service import TransactionService
from src.core.exception_handler import GlobalExceptionHandler

class SavingsService:
    """Lớp dịch vụ để quản lý tiết kiệm kỹ thuật số."""

    @staticmethod
    def create_plan(username: str, plan_name: str, savings_type: str, 
                    target_amount: float, duration_months: int) -> tuple[bool, str]:
        """Tạo một kế hoạch tiết kiệm mới cho người dùng."""
        conn = get_db_connection()
        if not conn:
            return False, "Database connection error."
        
        try:
            cursor = conn.cursor()
            
            # Xác định lãi suất
            # Linh hoạt: 0.1% / tháng (xấp xỉ) -> 1.2% / năm
            # Cố định: 0.5% / tháng (xấp xỉ) -> 6.0% / năm
            rate = 0.001 if savings_type == SavingsType.FLEXIBLE else 0.005
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_months * 30)
            
            plan = SavingsAccount(
                username=username,
                plan_name=plan_name,
                savings_type=savings_type,
                target_amount=target_amount,
                interest_rate=rate,
                duration_months=duration_months,
                start_date=start_date.strftime("%Y-%m-%d %H:%M:%S"),
                end_date=end_date.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            cursor.execute(
                """INSERT INTO savings_accounts 
                   (savings_id, username, plan_name, savings_type, target_amount, 
                    current_amount, interest_rate, duration_months, start_date, end_date, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (plan.savings_id, plan.username, plan.plan_name, plan.savings_type, 
                 plan.target_amount, plan.current_amount, plan.interest_rate, 
                 plan.duration_months, plan.start_date, plan.end_date, plan.status)
            )
            conn.commit()
            return True, "Savings plan created successfully."
        except Exception as e:
            conn.rollback()
            GlobalExceptionHandler.log_error(f"SavingsService.create_plan error:\n{traceback.format_exc()}")
            return False, f"Failed to create plan: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def deposit(username: str, savings_id: str, amount: float) -> tuple[bool, str]:
        """Gửi tiền từ ví vào tài khoản tiết kiệm."""
        if amount <= 0:
            return False, "Invalid deposit amount."

        # Giữ khóa ví tạm thời
        if not WalletService.lock_wallet_temporarily(username):
            return False, "Wallet is temporarily locked."

        conn = get_db_connection()
        if not conn:
            WalletService.unlock_wallet(username)
            return False, "Database connection error."

        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            # 1. Kiểm tra số dư ví
            cursor.execute("SELECT balance, account_status FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                raise Exception("User not found.")
            
            if row["account_status"] in ("FROZEN", "SUSPENDED"):
                raise Exception(f"Account is {row['account_status']}.")

            if float(row["balance"]) < amount:
                raise Exception("Insufficient wallet balance.")
            
            # 2. Kiểm tra kế hoạch tiết kiệm
            cursor.execute("SELECT current_amount, status FROM savings_accounts WHERE savings_id = ?", (savings_id,))
            plan_row = cursor.fetchone()
            if not plan_row:
                raise Exception("Savings plan not found.")
            
            if plan_row["status"] != SavingsStatus.ACTIVE:
                raise Exception("This savings plan is no longer active.")

            # 3. Cập nhật Ví
            new_wallet_balance = float(row["balance"]) - amount
            cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (new_wallet_balance, username))

            # 4. Cập nhật Tiết kiệm
            new_savings_amount = float(plan_row["current_amount"]) + amount
            cursor.execute(
                "UPDATE savings_accounts SET current_amount = ? WHERE savings_id = ?",
                (new_savings_amount, savings_id)
            )

            # 5. Ghi nhật ký Giao dịch Tiết kiệm
            TransactionService.create_savings_history(savings_id, amount, "DEPOSIT", conn)

            # 6. Ghi nhật ký lịch sử giao dịch chính của người dùng
            # Được xử lý bởi create_savings_transaction (độc lập bên dưới, hoặc chúng ta có thể truyền conn)
            # Để đảm bảo tính nguyên tử, hãy giữ nó trong cùng một giao dịch.
            from src.models.transaction_model import Transaction, TransactionStatus
            import uuid
            txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            cursor.execute(
                """INSERT INTO transactions
                   (transaction_id, sender_username, receiver_bank, receiver_account,
                    amount, note, status, transaction_type, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (txn_id, username, "Đăng Khoa Bank", f"SAVINGS-{savings_id}", amount, 
                 f"Deposit to savings: {savings_id}", TransactionStatus.SUCCESS, "SAVINGS_DEPOSIT", 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            # 7. Ghi nhật ký Kiểm tra của Quản trị viên
            TransactionService.create_admin_savings_log("SYSTEM", "SAVINGS_DEPOSIT", username, f"Deposited {amount} to {savings_id}", conn)

            conn.commit()
            
            # Tác dụng phụ: Thông báo
            try:
                NotificationService.create_notification(
                    username,
                    "Savings Deposit Success",
                    f"Successfully deposited {amount:,.0f} VND to your savings plan {savings_id}.",
                    "SAVINGS"
                )
            except: pass

            return True, f"Deposited {amount:,.0f} VND into {savings_id}."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
            WalletService.unlock_wallet(username)

    @staticmethod
    def withdraw(username: str, savings_id: str, amount: float) -> tuple[bool, str]:
        """Rút tiền từ tài khoản tiết kiệm về ví."""
        if amount <= 0:
            return False, "Invalid withdrawal amount."

        # Giữ khóa ví tạm thời
        if not WalletService.lock_wallet_temporarily(username):
            return False, "Wallet is temporarily locked."

        conn = get_db_connection()
        if not conn:
            WalletService.unlock_wallet(username)
            return False, "Database connection error."

        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            # 1. Kiểm tra kế hoạch tiết kiệm
            cursor.execute(
                "SELECT current_amount, status, savings_type, end_date FROM savings_accounts WHERE savings_id = ?", 
                (savings_id,)
            )
            plan_row = cursor.fetchone()
            if not plan_row:
                raise Exception("Savings plan not found.")
            
            if float(plan_row["current_amount"]) < amount:
                raise Exception("Insufficient savings balance.")

            # 2. Kiểm tra các quy tắc kỳ hạn cố định
            if plan_row["savings_type"] == SavingsType.FIXED:
                end_date = datetime.strptime(plan_row["end_date"], "%Y-%m-%d %H:%M:%S")
                if datetime.now() < end_date:
                    raise Exception("Fixed savings plan has not matured yet.")

            # 3. Cập nhật Tiết kiệm
            new_savings_amount = float(plan_row["current_amount"]) - amount
            cursor.execute(
                "UPDATE savings_accounts SET current_amount = ? WHERE savings_id = ?",
                (new_savings_amount, savings_id)
            )
            
            if new_savings_amount <= 0.01: # Sử dụng ngưỡng nhỏ để so sánh số thực
                cursor.execute("UPDATE savings_accounts SET status = ? WHERE savings_id = ?", (SavingsStatus.COMPLETED, savings_id))

            # 4. Cập nhật Ví
            cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            new_wallet_balance = float(user_row["balance"]) + amount
            cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (new_wallet_balance, username))

            # 5. Ghi nhật ký Giao dịch Tiết kiệm
            TransactionService.create_savings_history(savings_id, amount, "WITHDRAWAL", conn)

            # 6. Ghi nhật ký lịch sử giao dịch chính của người dùng
            from src.models.transaction_model import Transaction, TransactionStatus
            import uuid
            txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            cursor.execute(
                """INSERT INTO transactions
                   (transaction_id, sender_username, receiver_bank, receiver_account,
                    amount, note, status, transaction_type, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (txn_id, username, "SAVINGS", "WALLET", amount, 
                 f"Withdraw from savings: {savings_id}", TransactionStatus.SUCCESS, "SAVINGS_WITHDRAWAL", 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            # 7. Ghi nhật ký Kiểm tra của Quản trị viên
            TransactionService.create_admin_savings_log("SYSTEM", "SAVINGS_WITHDRAWAL", username, f"Withdrew {amount} from {savings_id}", conn)

            conn.commit()

            # Tác dụng phụ: Thông báo
            try:
                NotificationService.create_notification(
                    username,
                    "Savings Withdrawal Success",
                    f"Successfully withdrew {amount:,.0f} VND from your savings plan {savings_id} to your wallet.",
                    "SAVINGS"
                )
            except: pass

            return True, f"Withdrew {amount:,.0f} VND from savings."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
            WalletService.unlock_wallet(username)

    @staticmethod
    def get_user_plans(username: str) -> list[SavingsAccount]:
        """Lấy tất cả các kế hoạch tiết kiệm cho một người dùng."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM savings_accounts WHERE username = ? ORDER BY created_at DESC", (username,))
            rows = cursor.fetchall()
            return [SavingsAccount.from_db_row(dict(row)) for row in rows]
        except Exception as e:
            print(f"SavingsService.get_user_plans error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_savings_stats(username: str) -> dict:
        """Lấy số liệu thống kê tóm tắt cho tiền tiết kiệm của người dùng."""
        conn = get_db_connection()
        if not conn:
            return {"total_saved": 0.0, "active_count": 0, "total_interest": 0.0}
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT SUM(current_amount) as total_saved, 
                          COUNT(*) as active_count,
                          SUM(current_amount * interest_rate) as estimated_interest
                   FROM savings_accounts 
                   WHERE username = ? AND status = 'ACTIVE'""",
                (username,)
            )
            row = cursor.fetchone()
            return {
                "total_saved": float(row["total_saved"] or 0),
                "active_count": int(row["active_count"] or 0),
                "total_interest": float(row["estimated_interest"] or 0)
            }
        except Exception as e:
            print(f"SavingsService.get_savings_stats error: {e}")
            return {"total_saved": 0.0, "active_count": 0, "total_interest": 0.0}
        finally:
            conn.close()

    @staticmethod
    def get_savings_history(savings_id: str) -> list:
        """Lấy lịch sử giao dịch cho một kế hoạch tiết kiệm cụ thể."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM savings_transactions WHERE savings_id = ? ORDER BY created_at DESC",
                (savings_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"SavingsService.get_savings_history error: {e}")
            return []
        finally:
            conn.close()
