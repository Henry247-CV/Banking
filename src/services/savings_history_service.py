from src.database.database import get_db_connection
from src.models.savings_model import SavingsTransaction

class SavingsHistoryService:
    @staticmethod
    def get_combined_history(username):
        """Returns all savings-related activities for a user."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Fetch from savings_transactions
            cursor.execute("""
                SELECT st.*, sa.plan_name 
                FROM savings_transactions st
                JOIN savings_accounts sa ON st.savings_id = sa.id
                WHERE st.username = ?
                ORDER BY st.created_at DESC
            """, (username,))
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Combined history error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def log_savings_action(username, savings_id, amount, action_type):
        """Internal helper to log to both savings and main transaction tables."""
        from src.services.transaction_service import TransactionService
        from src.models.transaction_model import Transaction, TransactionStatus, TransactionType
        
        # 1. Log to savings_transactions table
        TransactionService.create_savings_history(savings_id, amount, action_type)
        
        # 2. Log to main transactions table for general history
        TransactionService.create_savings_transaction(username, savings_id, amount, action_type)
