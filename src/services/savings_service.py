import sqlite3
import traceback
from datetime import datetime, timedelta
from src.database.database import get_db_connection
from src.models.savings_model import SavingsAccount, SavingsTransaction
from src.core.debug_logger import DebugLogger

class SavingsService:
    @staticmethod
    def create_savings_plan(username, plan_name, savings_type, target_amount, duration_months, interest_rate):
        conn = get_db_connection()
        if not conn: return False, "Database connection error"
        
        try:
            cursor = conn.cursor()
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30 * duration_months)
            
            cursor.execute("""
                INSERT INTO savings_accounts 
                (username, plan_name, savings_type, target_amount, interest_rate, duration_months, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, plan_name, savings_type, target_amount, interest_rate, 
                  duration_months, start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S'), 'ACTIVE'))
            conn.commit()
            return True, "Savings plan created successfully"
        except Exception as e:
            DebugLogger.log_sqlite_error(e, context="CREATE_SAVINGS_PLAN")
            return False, f"Error creating plan: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_user_savings(username):
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM savings_accounts WHERE username = ? ORDER BY created_at DESC", (username,))
            rows = cursor.fetchall()
            return [SavingsAccount.from_db_row(row) for row in rows]
        except Exception as e:
            DebugLogger.log_sqlite_error(e, context="GET_USER_SAVINGS")
            return []
        finally:
            conn.close()

    @staticmethod
    def deposit(savings_id, username, amount):
        if amount <= 0: return False, "Amount must be positive"
        
        conn = get_db_connection()
        if not conn: return False, "Database connection error"
        
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            
            # 1. Check user balance
            cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            if not user_row or user_row['balance'] < amount:
                conn.rollback()
                return False, "Insufficient balance in wallet"
            
            # 2. Update wallet
            cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, username))
            
            # 3. Update savings account
            cursor.execute("UPDATE savings_accounts SET current_amount = current_amount + ? WHERE id = ?", (amount, savings_id))
            
            # 4. Log transaction (Synchronized)
            cursor.execute("""
                INSERT INTO savings_transactions (savings_id, username, type, amount)
                VALUES (?, ?, ?, ?)
            """, (savings_id, username, 'DEPOSIT', amount))
            
            # Also log to main transactions for admin/user history
            from src.services.transaction_service import TransactionService
            TransactionService.create_savings_transaction(username, savings_id, amount, 'DEPOSIT')
            
            conn.commit()
            return True, "Deposit successful"
        except Exception as e:
            if conn: 
                try: conn.rollback()
                except Exception: pass
            DebugLogger.log_sqlite_error(e, context="SAVINGS_DEPOSIT")
            return False, f"Deposit error: {str(e)}"
        finally:
            if conn: conn.close()

    @staticmethod
    def withdraw(savings_id, username, amount):
        if amount <= 0: return False, "Amount must be positive"
        
        conn = get_db_connection()
        if not conn: return False, "Database connection error"
        
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            
            # 1. Check savings account
            cursor.execute("SELECT * FROM savings_accounts WHERE id = ?", (savings_id,))
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                return False, "Savings account not found"
            
            account = SavingsAccount.from_db_row(row)
            if account.current_amount < amount:
                conn.rollback()
                return False, "Insufficient funds in savings account"
            
            # 2. Check fixed-term rules
            if account.savings_type == 'FIXED':
                end_date = datetime.strptime(account.end_date, '%Y-%m-%d %H:%M:%S')
                if datetime.now() < end_date:
                    conn.rollback()
                    return False, f"Fixed-term plan matures on {account.end_date[:10]}. Early withdrawal is locked."

            # 3. Update savings account
            cursor.execute("UPDATE savings_accounts SET current_amount = current_amount - ? WHERE id = ?", (amount, savings_id))
            
            # 4. Update wallet
            cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, username))
            
            # 5. Log transaction
            cursor.execute("""
                INSERT INTO savings_transactions (savings_id, username, type, amount)
                VALUES (?, ?, ?, ?)
            """, (savings_id, username, 'WITHDRAWAL', amount))
            
            from src.services.transaction_service import TransactionService
            TransactionService.create_savings_transaction(username, savings_id, amount, 'WITHDRAWAL')
            
            conn.commit()
            return True, "Withdrawal successful"
        except Exception as e:
            if conn: 
                try: conn.rollback()
                except Exception: pass
            DebugLogger.log_sqlite_error(e, context="SAVINGS_WITHDRAW")
            return False, f"Withdrawal error: {str(e)}"
        finally:
            if conn: conn.close()

    @staticmethod
    def get_savings_history(username, savings_id=None):
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            if savings_id:
                cursor.execute("SELECT * FROM savings_transactions WHERE savings_id = ? ORDER BY created_at DESC", (savings_id,))
            else:
                cursor.execute("SELECT * FROM savings_transactions WHERE username = ? ORDER BY created_at DESC", (username,))
            rows = cursor.fetchall()
            return [SavingsTransaction(**dict(row)) for row in rows]
        except Exception:
            return []
        finally:
            conn.close()

    @staticmethod
    def get_savings_stats(username):
        savings = SavingsService.get_user_savings(username)
        total_saved = sum(s.current_amount for s in savings)
        active_plans = len([s for s in savings if s.status == 'ACTIVE'])
        
        # Total interest earned across all plans
        total_interest = sum(s.interest_earned for s in savings)
        
        # Monthly interest estimation (simulated based on rates)
        monthly_interest = sum((s.current_amount * s.interest_rate / 12) for s in savings)
        
        return {
            "total_saved": total_saved,
            "active_plans": active_plans,
            "monthly_interest": monthly_interest,
            "total_interest": total_interest,
            "growth_rate": 5.4 # Mock growth rate
        }

    @staticmethod
    def add_interest_growth(savings_id, amount):
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # Update current amount and interest_earned
            cursor.execute("""
                UPDATE savings_accounts 
                SET current_amount = current_amount + ?,
                    interest_earned = interest_earned + ?,
                    last_growth_update = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (amount, amount, savings_id))
            
            # Log transaction
            cursor.execute("""
                INSERT INTO savings_transactions (savings_id, username, type, amount)
                SELECT id, username, 'INTEREST', ? FROM savings_accounts WHERE id = ?
            """, (amount, savings_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Interest growth error: {e}")
            return False
        finally:
            conn.close()
