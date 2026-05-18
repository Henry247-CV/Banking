import re
from datetime import datetime, timedelta
from src.database.database import get_db_connection
from src.security import security_rules
from src.admin.services.security_service import SecurityService

class SecurityManager:
    @staticmethod
    def validate_password_strength(password):
        """Validates password against security rules."""
        if len(password) < security_rules.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {security_rules.MIN_PASSWORD_LENGTH} characters long."
        if security_rules.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if security_rules.REQUIRE_NUMBER and not re.search(r"\d", password):
            return False, "Password must contain at least one number."
        return True, "Valid password"

    @staticmethod
    def setup_security_pin(username, pin):
        """Sets a security PIN for a user."""
        if len(pin) != security_rules.PIN_LENGTH or not pin.isdigit():
            return False, f"PIN must be exactly {security_rules.PIN_LENGTH} digits."
            
        conn = get_db_connection()
        if not conn: return False, "DB Error"
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET security_pin = ? WHERE username = ?", (pin, username))
            conn.commit()
            return True, "Security PIN successfully configured."
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            conn.close()

    @staticmethod
    def verify_security_pin(username, pin):
        """Verifies a user's security PIN."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT security_pin FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and row[0]:
                return row[0] == pin
            return False
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def check_account_status(username):
        """Checks if account is locked due to failed attempts."""
        conn = get_db_connection()
        if not conn: return False, "DB Error"
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT failed_attempts, account_locked_until FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row: return True, "User not found" # Handled elsewhere
            
            locked_until = row[1]
            if locked_until:
                lock_time = datetime.strptime(locked_until, "%Y-%m-%d %H:%M:%S")
                if datetime.now() < lock_time:
                    return False, f"Account temporarily locked for security reasons until {locked_until}."
                else:
                    # Lock expired, reset
                    cursor.execute("UPDATE users SET failed_attempts = 0, account_locked_until = NULL WHERE username = ?", (username,))
                    conn.commit()
            return True, "Account is accessible"
        except Exception as e:
            return False, f"Error checking account status: {e}"
        finally:
            conn.close()

    @staticmethod
    def track_failed_attempt(username):
        """Increments failed attempts and locks account if threshold reached."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT failed_attempts FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                failed = (row[0] or 0) + 1
                now = datetime.now()
                
                if failed >= security_rules.MAX_LOGIN_ATTEMPTS:
                    lock_until = now + timedelta(minutes=security_rules.ACCOUNT_LOCK_DURATION_MINUTES)
                    cursor.execute(
                        "UPDATE users SET failed_attempts = ?, last_failed_attempt = ?, account_locked_until = ? WHERE username = ?",
                        (failed, now.strftime("%Y-%m-%d %H:%M:%S"), lock_until.strftime("%Y-%m-%d %H:%M:%S"), username)
                    )
                    SecurityService.log_admin_action("SYSTEM", "AUTO_LOCK_ACCOUNT", f"User:{username} (Max failed logins)")
                else:
                    cursor.execute(
                        "UPDATE users SET failed_attempts = ?, last_failed_attempt = ? WHERE username = ?",
                        (failed, now.strftime("%Y-%m-%d %H:%M:%S"), username)
                    )
                conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def reset_failed_attempts(username):
        """Resets failed login attempts after a successful login."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET failed_attempts = 0, account_locked_until = NULL WHERE username = ?", (username,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def is_session_expired(last_activity_time_str):
        """Checks if a session should be timed out due to inactivity."""
        if not last_activity_time_str: return True
        try:
            last_activity = datetime.strptime(last_activity_time_str, "%Y-%m-%d %H:%M:%S")
            expiry_time = last_activity + timedelta(minutes=security_rules.SESSION_TIMEOUT_MINUTES)
            return datetime.now() > expiry_time
        except Exception:
            return True
