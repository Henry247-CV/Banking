from src.database.database import get_db_connection

class SavingService:
    @staticmethod
    def create_saving_goal(username, goal_name, target_amount):
        """Creates a new saving goal for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO savings (username, goal_name, target_amount) VALUES (?, ?, ?)",
                (username, goal_name, target_amount)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Saving goal error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_savings(username):
        """Retrieves all saving goals for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, goal_name, target_amount, current_amount, status, created_at FROM savings WHERE username = ? ORDER BY created_at DESC",
            (username,)
        )
        savings = cursor.fetchall()
        conn.close()
        return savings

    @staticmethod
    def update_saving_amount(goal_id, amount):
        """Adds an amount to an existing saving goal."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE savings SET current_amount = current_amount + ? WHERE id = ?",
                (amount, goal_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Update saving error: {e}")
            return False
        finally:
            conn.close()
