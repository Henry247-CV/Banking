import os
import sqlite3
import shutil
import json
import csv
from datetime import datetime
from src.database.database import get_db_connection, DB_PATH
from src.admin.services.security_service import SecurityService

class BackupService:
    BACKUP_DIR = "backups"
    EXPORT_DIR = "exports"

    @classmethod
    def _ensure_dirs(cls):
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
        os.makedirs(cls.EXPORT_DIR, exist_ok=True)

    @classmethod
    def create_backup(cls, admin_username="admin"):
        """Creates a safe local copy of the SQLite database."""
        cls._ensure_dirs()
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(cls.BACKUP_DIR, backup_filename)
        
        try:
            # We can use sqlite3 backup API for safe copying while DB is open
            src = sqlite3.connect(DB_PATH)
            dst = sqlite3.connect(backup_path)
            with dst:
                src.backup(dst)
            dst.close()
            src.close()
            
            SecurityService.log_admin_action(admin_username, "CREATE_BACKUP", f"File:{backup_filename}")
            return True, f"Backup created successfully: {backup_filename}"
        except Exception as e:
            return False, f"Failed to create backup: {e}"

    @classmethod
    def restore_backup(cls, backup_filename, admin_username="admin"):
        """Restores a backup, creating a safety copy of the current DB first."""
        cls._ensure_dirs()
        backup_path = os.path.join(cls.BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            return False, "Backup file not found."
            
        try:
            # Create safety backup first
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            safety_backup = os.path.join(cls.BACKUP_DIR, f"safety_pre_restore_{timestamp}.db")
            shutil.copy2(DB_PATH, safety_backup)
            
            # Replace current DB
            shutil.copy2(backup_path, DB_PATH)
            
            SecurityService.log_admin_action(admin_username, "RESTORE_BACKUP", f"Restored:{backup_filename}")
            return True, "Database restored successfully. Please restart the application."
        except Exception as e:
            return False, f"Restore failed: {e}"

    @classmethod
    def get_backup_history(cls):
        """Returns a list of available backups in the backup directory."""
        cls._ensure_dirs()
        backups = []
        try:
            for filename in os.listdir(cls.BACKUP_DIR):
                if filename.endswith(".db"):
                    filepath = os.path.join(cls.BACKUP_DIR, filename)
                    stats = os.stat(filepath)
                    size_mb = stats.st_size / (1024 * 1024)
                    created_at = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    backups.append({
                        "filename": filename,
                        "created_at": created_at,
                        "size_mb": round(size_mb, 2),
                        "status": "Ready"
                    })
            # Sort newest first
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            return backups
        except Exception as e:
            print(f"Error getting backups: {e}")
            return []
            
    @classmethod
    def delete_backup(cls, backup_filename, admin_username="admin"):
        """Deletes a specific backup file."""
        backup_path = os.path.join(cls.BACKUP_DIR, backup_filename)
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                SecurityService.log_admin_action(admin_username, "DELETE_BACKUP", f"File:{backup_filename}")
                return True
            return False
        except Exception as e:
            print(f"Failed to delete backup: {e}")
            return False

    @classmethod
    def cleanup_temp_files(cls, admin_username="admin"):
        """Cleans up old TXT files, expired sessions, and old notifications."""
        deleted_files = 0
        try:
            # 1. Cleanup TXT files in root (verification codes)
            for f in os.listdir("."):
                if f.endswith(".txt") and ("verification" in f or "activation" in f):
                    # Check age
                    stat = os.stat(f)
                    age_hours = (datetime.now().timestamp() - stat.st_mtime) / 3600
                    if age_hours > 24: # older than 24h
                        os.remove(f)
                        deleted_files += 1
            
            # 2. Cleanup old inactive sessions & read notifications from DB
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM active_sessions WHERE status != 'ACTIVE'")
                cursor.execute("DELETE FROM notifications WHERE is_read = 1 AND created_at < datetime('now', '-7 days')")
                conn.commit()
                conn.close()
                
            SecurityService.log_admin_action(admin_username, "SYSTEM_CLEANUP", f"Deleted {deleted_files} files + DB cleanup")
            return True, f"Cleanup complete. Deleted {deleted_files} old files."
        except Exception as e:
            return False, f"Cleanup failed: {e}"

    @classmethod
    def export_logs(cls, log_type="security", format="csv", admin_username="admin"):
        """Exports specific system logs to the exports directory."""
        cls._ensure_dirs()
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        filename = f"export_{log_type}_{timestamp}.{format}"
        filepath = os.path.join(cls.EXPORT_DIR, filename)
        
        conn = get_db_connection()
        if not conn: return False, "DB connection failed"
        
        try:
            cursor = conn.cursor()
            if log_type == "security":
                cursor.execute("SELECT * FROM admin_logs ORDER BY created_at DESC")
            elif log_type == "transactions":
                cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC")
            elif log_type == "users":
                cursor.execute("SELECT id, username, full_name, email, account_status, customer_tier FROM users")
            else:
                return False, "Invalid log type"
                
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if format == "csv":
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)
            elif format == "json":
                data = [dict(zip(columns, row)) for row in rows]
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                return False, "Invalid format"
                
            SecurityService.log_admin_action(admin_username, "EXPORT_LOGS", f"Type:{log_type}, Format:{format}")
            return True, f"Exported successfully to {filepath}"
        except Exception as e:
            return False, f"Export failed: {e}"
        finally:
            conn.close()

    @classmethod
    def get_maintenance_mode(cls):
        """Checks if emergency maintenance mode is active."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_settings WHERE key = 'maintenance_mode'")
            row = cursor.fetchone()
            if row:
                return row[0] == "true"
            return False
        except Exception:
            return False
        finally:
            conn.close()

    @classmethod
    def toggle_maintenance_mode(cls, admin_username="admin"):
        """Toggles emergency maintenance mode."""
        current_mode = cls.get_maintenance_mode()
        new_mode = "false" if current_mode else "true"
        
        conn = get_db_connection()
        if not conn: return False, "DB Error"
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE system_settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = 'maintenance_mode'",
                (new_mode,)
            )
            conn.commit()
            action = "DISABLED" if current_mode else "ENABLED"
            SecurityService.log_admin_action(admin_username, f"MAINTENANCE_{action}", "System Maintenance Mode")
            return True, f"Maintenance mode {action.lower()}."
        except Exception as e:
            return False, f"Failed to toggle mode: {e}"
        finally:
            conn.close()
