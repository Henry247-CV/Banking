import random
import os
from datetime import datetime
from pathlib import Path
from src.database.database import get_db_connection
from src.services.notification_service import NotificationService
from src.admin.services.security_service import SecurityService
from src.security.security_manager import SecurityManager

class AuthService:
    @staticmethod
    def login_user(username, password):
        """Checks if the username and password match. Returns user dict or None.
        
        Account status enforcement:
        - SUSPENDED: login blocked, returns special error dict
        - FROZEN: login allowed, but flag is set in returned data
        - ACTIVE: normal login
        """
        # Security: Check if account is locked due to failed attempts
        is_accessible, lock_msg = SecurityManager.check_account_status(username)
        if not is_accessible:
            return {"error": "locked", "message": lock_msg}

        conn = get_db_connection()
        if not conn: return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            user_row = cursor.fetchone()
            if not user_row:
                # Track failed attempt
                SecurityService.track_login_attempt(username, "FAILED")
                SecurityManager.track_failed_attempt(username)
                return None
            
            user_data = dict(user_row)
            
            # Check account status
            account_status = user_data.get("account_status", "ACTIVE") or "ACTIVE"
            
            if account_status == "SUSPENDED":
                SecurityService.track_login_attempt(username, "BLOCKED")
                return {"error": "suspended", "message": "Your account has been suspended."}
            
            # Reset failed attempts on success
            SecurityManager.reset_failed_attempts(username)
            
            # Update last_login timestamp and log success
            try:
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
                    (username,)
                )
                conn.commit()
            except Exception:
                pass  # Non-critical, don't block login
                
            SecurityService.track_login_attempt(username, "SUCCESS")
            # Create active session and attach token
            token = SecurityService.create_session(username)
            if token:
                user_data["session_token"] = token
            
            return user_data
        except Exception as e:
            print(f"Login error: {e}")
            SecurityService.track_login_attempt(username, "ERROR")
            return None
        finally:
            conn.close()

    @staticmethod
    def is_username_taken(username):
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def is_cccd_taken(cccd):
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE cccd = ?", (cccd,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def generate_account_number():
        """Generates a unique account number in DKB + YEAR + RANDOM format."""
        year = datetime.now().year
        while True:
            random_digits = random.randint(1000, 9999)
            acc_num = f"DKB{year}{random_digits}"
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE account_number = ?", (acc_num,))
            if not cursor.fetchone():
                conn.close()
                return acc_num
            conn.close()

    @staticmethod
    def generate_verification_code():
        code = str(random.randint(100000, 999999))
        desktop_path = Path.home() / "Desktop"
        file_path = desktop_path / f"verification_{code}.txt"

        content = f"""ĐĂNG KHOA BANK VERIFICATION CODE\n\nYour login verification code:\n\n{code}\n\nDo not share this code."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            if os.name == 'nt': os.startfile(file_path)
        except Exception as e:
            print(f"File error: {e}")
        return code, file_path

    @staticmethod
    def generate_activation_code():
        code = str(random.randint(100000, 999999))
        desktop_path = Path.home() / "Desktop"
        file_path = desktop_path / f"activation_{code}.txt"

        content = f"""ĐĂNG KHOA BANK ACTIVATION CODE\n\nWelcome to Đăng Khoa Bank\n\nYour activation code:\n\n{code}\n\nPlease enter this code to activate your account."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            if os.name == 'nt': os.startfile(file_path)
        except Exception as e:
            print(f"File error: {e}")
        return code, file_path
    @staticmethod
    def register_user(username, password, full_name, phone, cccd, email=""):
        """Registers a user with their phone number as the account number."""
        is_valid, msg = SecurityManager.validate_password_strength(password)
        if not is_valid:
            print(f"Password validation failed: {msg}")
            return False

        # STK equivalent to Phone Number
        acc_num = phone 
        conn = get_db_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users (username, password, full_name, phone, cccd, email, account_number) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (username, password, full_name, phone, cccd, email, acc_num)
            )
            conn.commit()
            NotificationService.create_notification(
                username, 
                "Account Activated", 
                f"Welcome! Your phone number {phone} is now your bank account number. Enjoy our premium services.",
                "SUCCESS"
            )
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update_password(user_id, username, new_password):
        is_valid, msg = SecurityManager.validate_password_strength(new_password)
        if not is_valid:
            print(f"Password validation failed: {msg}")
            return False

        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
            conn.commit()
            NotificationService.create_notification(username, "Security Update", "Your password has been changed successfully.", "SECURITY")
            return True
        except Exception as e:
            print(f"Password update error: {e}")
            return False
        finally:
            conn.close()
