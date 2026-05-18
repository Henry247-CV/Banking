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

            # 2. Subtract balance
            cursor.execute(
                "UPDATE users SET balance = ? WHERE username = ?",
                (new_balance, sender_username)
            )

            # 3. Record transaction
            cursor.execute(
                """INSERT INTO transactions (sender_username, receiver_bank, receiver_account, amount, note)
                   VALUES (?, ?, ?, ?, ?)""",
                (sender_username, receiver_bank, receiver_account, amount, note)
            )

            conn.commit()
            
            # Auto-update tier after balance change
            TierService.update_user_tier(sender_username, new_balance)

            # Notify transfer success
            NotificationService.create_notification(
                sender_username,
                "Transfer Successful",
                f"You have successfully transferred {"{:,.0f}".format(amount)} VND to {receiver_bank} account {receiver_account}.",
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
        """Retrieves all transactions for a specific user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT created_at, receiver_bank, receiver_account, amount, status FROM transactions WHERE sender_username = ? ORDER BY created_at DESC",
            (username,)
        )
        transactions = cursor.fetchall()
        conn.close()
        return transactions

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
