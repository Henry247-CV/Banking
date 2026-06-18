import os
from datetime import datetime
from pathlib import Path
from src.database.database import get_db_connection
from src.services.notification_service import NotificationService
from src.services.tier_service import TierService

class TransferService:
    @staticmethod
    def create_transfer(sender_username, receiver_bank, receiver_account, amount, note):
        """Processes a transfer: updates balance and records transaction."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 0. Check account status — block frozen/suspended accounts
            cursor.execute(
                "SELECT balance, account_status FROM users WHERE username = ?",
                (sender_username,)
            )
            user_row = cursor.fetchone()
            if not user_row:
                return False, "User not found."
            
            account_status = user_row[1] if user_row[1] else "ACTIVE"
            if account_status == "FROZEN":
                return False, "Your account is temporarily frozen. Transfers are disabled."
            if account_status == "SUSPENDED":
                return False, "Your account has been suspended. Please contact support."
            
            # 1. Check sender balance
            if user_row[0] < amount:
                return False, "Insufficient balance."

            new_balance = user_row[0] - amount

            # If internal, look up and validate receiver
            is_internal = receiver_bank in ("Đăng Khoa Bank", "DKB")
            receiver_username = None
            new_receiver_balance = None
            if is_internal:
                cursor.execute(
                    "SELECT username, balance, account_status FROM users WHERE account_number = ? OR phone = ?",
                    (receiver_account.strip(), receiver_account.strip())
                )
                receiver_row = cursor.fetchone()
                if not receiver_row:
                    return False, f"Receiver account '{receiver_account}' not found in Đăng Khoa Bank."
                
                receiver_username = receiver_row["username"]
                receiver_status = receiver_row["account_status"] or "ACTIVE"
                if receiver_status in ("FROZEN", "SUSPENDED"):
                    return False, "Receiver account is not available for transfers."
                if receiver_username == sender_username:
                    return False, "You cannot transfer to your own account."
                
                new_receiver_balance = float(receiver_row["balance"]) + amount

            # 2. Update balances
            cursor.execute(
                "UPDATE users SET balance = ? WHERE username = ?",
                (new_balance, sender_username)
            )
            if is_internal and receiver_username:
                cursor.execute(
                    "UPDATE users SET balance = ? WHERE username = ?",
                    (new_receiver_balance, receiver_username)
                )

            # 3. Record transaction
            from src.admin.services.admin_transaction_service import AdminTransactionService
            import uuid
            
            risk_level = AdminTransactionService.calculate_risk_level(amount, sender_username)
            flagged = 1 if risk_level in ("HIGH", "CRITICAL") else 0
            review_status = "REVIEWING" if flagged else "COMPLETED"
            txn_id = f"TXN-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
            txn_type = "TRANSFER"
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """INSERT INTO transactions 
                   (transaction_id, sender_username, receiver_bank, receiver_account, 
                    amount, note, status, transaction_type, flagged, risk_level, review_status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (txn_id, sender_username, receiver_bank, receiver_account, 
                 amount, note, "SUCCESS", txn_type, flagged, risk_level, review_status, created_at)
            )

            conn.commit()
            
            # Auto-update tiers after balance change
            TierService.update_user_tier(sender_username, new_balance)
            if is_internal and receiver_username:
                TierService.update_user_tier(receiver_username, new_receiver_balance)

            # Notify transfer success (sender)
            NotificationService.create_notification(
                sender_username,
                "Transfer Successful",
                f"You have successfully transferred {"{:,.0f}".format(amount)} VND to {receiver_bank} account {receiver_account}.",
                "TRANSFER"
            )

            # Notify transfer success (receiver)
            if is_internal and receiver_username:
                NotificationService.create_notification(
                    receiver_username,
                    "Money Received",
                    f"You received {"{:,.0f}".format(amount)} VND from {sender_username}.",
                    "TRANSFER"
                )
            
            return True, "Transfer successful."
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_user_transactions(username):
        """Retrieves all transactions for a specific user (both sent and received)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Fetch user's account_number and phone to identify received transactions
        cursor.execute("SELECT account_number, phone FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            return []
            
        account_number = user_row["account_number"]
        phone = user_row["phone"]
        
        # 2. Query transactions where the user is either sender OR receiver
        cursor.execute(
            """
            SELECT t.created_at, t.receiver_bank, t.receiver_account, t.amount, t.status, 
                   t.sender_username, u_sender.account_number AS sender_account_num
            FROM transactions t
            LEFT JOIN users u_sender ON t.sender_username = u_sender.username
            WHERE t.sender_username = ?
               OR (t.receiver_bank IN ('Đăng Khoa Bank', 'DKB') AND (t.receiver_account = ? OR t.receiver_account = ?))
            ORDER BY t.created_at DESC
            """,
            (username, account_number, phone)
        )
        rows = cursor.fetchall()
        conn.close()
        
        # 3. Format rows to match the expected return tuple format
        formatted = []
        for r in rows:
            created_at, receiver_bank, receiver_account, amount, status, sender_username, sender_account_num = r
            if sender_username == username:
                # Outgoing: amount is positive, so caller's negation (-amount) makes it negative/red
                formatted.append((created_at, receiver_bank, receiver_account, amount, status))
            else:
                # Incoming: amount is negated, so caller's negation (-amount) makes it positive/green
                display_acc = sender_account_num if sender_account_num else sender_username
                formatted.append((created_at, "Đăng Khoa Bank", display_acc, -amount, status))
                
        return formatted

    @staticmethod
    def generate_transfer_bill(sender_username, receiver_bank, receiver_account, amount, note):
        """Generates a TXT bill on the Desktop and opens it."""
        desktop_path = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        file_name = f"transfer_bill_{timestamp}.txt"
        file_path = desktop_path / file_name

        content = f"""ĐĂNG KHOA BANK TRANSFER BILL

Sender:
{sender_username}

Receiver Bank:
{receiver_bank}

Receiver Account:
{receiver_account}

Amount:
{"{:,.0f} VND".format(amount)}

Note:
{note if note else "N/A"}

Status:
SUCCESS

Date:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            if os.name == 'nt':
                os.startfile(file_path)
            return True
        except Exception as e:
            print(f"Bill generation error: {e}")
            return False
