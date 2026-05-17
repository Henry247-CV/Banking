from src.database.database import get_db_connection

class TierService:
    @staticmethod
    def calculate_customer_tier(balance):
        """Determines customer tier based on balance."""
        if balance >= 100000000.0: # 100M VND
            return "DIAMOND"
        elif balance >= 20000000.0: # 20M VND
            return "GOLD"
        else:
            return "STANDARD"

    @staticmethod
    def update_user_tier(username, balance):
        """Calculates and updates the user's tier in the database if it has changed."""
        new_tier = TierService.calculate_customer_tier(balance)
        
        conn = get_db_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            # Check current tier first to avoid unnecessary updates
            cursor.execute("SELECT customer_tier FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and row[0] == new_tier:
                return True # No change needed
            
            cursor.execute(
                "UPDATE users SET customer_tier = ? WHERE username = ?",
                (new_tier, username)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Tier update error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_tier_benefits(tier):
        """Returns benefits text based on tier."""
        if tier == "DIAMOND":
            return [
                "● Priority 24/7 Elite Support",
                "● Unlimited Transfer Limits",
                "● Zero Transaction Fees",
                "● Exclusive Airport Lounges"
            ]
        elif tier == "GOLD":
            return [
                "● Priority Banking Support",
                "● High Transfer Limits",
                "● Reduced Transaction Fees",
                "● Cashback Rewards"
            ]
        else:
            return [
                "● 24/7 Digital Support",
                "● Standard Transfer Limits",
                "● Secure Online Banking",
                "● Local Branch Access"
            ]
