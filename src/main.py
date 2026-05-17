import sys
import os

# Add the project root directory to sys.path to allow absolute imports from 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QStackedWidget
from src.database.database import init_db
from src.ui.login_window import LoginWindow
from src.ui.register_window import RegisterWindow
from src.ui.dashboard_window import DashboardWindow

from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager
from src.core.styles import get_styles

class BankingApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        
        self.login_window = LoginWindow()
        self.register_window = RegisterWindow()
        self.dashboard_window = None # Initialize after login
        
        self.addWidget(self.login_window)
        self.addWidget(self.register_window)
        
        # Connections
        self.login_window.switch_to_register.connect(lambda: self.setCurrentWidget(self.register_window))
        self.register_window.switch_to_login.connect(lambda: self.setCurrentWidget(self.login_window))
        self.login_window.login_success.connect(self.show_dashboard)
        
        self.lang_manager.language_changed.connect(self.update_translations)
        self.theme_manager.theme_changed.connect(self.update_theme)

        self.setWindowTitle("Đăng Khoa Bank")
        self.resize(1200, 720)
        self.update_theme()
        self.update_translations()

    def update_theme(self):
        styles = get_styles()
        self.setStyleSheet(styles["GLOBAL_STYLE"])
        if hasattr(self.login_window, "update_theme"):
            self.login_window.update_theme()
        if hasattr(self.register_window, "update_theme"):
            self.register_window.update_theme()

    def update_translations(self):
        if hasattr(self.login_window, "update_translations"):
            self.login_window.update_translations()
        if hasattr(self.register_window, "update_translations"):
            self.register_window.update_translations()

    def show_dashboard(self, user_data):
        # Create dashboard window with user data
        self.dashboard_window = DashboardWindow(user_data)
        self.addWidget(self.dashboard_window)
        
        # Connect logout
        self.dashboard_window.logout_requested.connect(self.logout)
        
        self.setCurrentWidget(self.dashboard_window)
        self.setWindowTitle("Đăng Khoa Bank - Dashboard")

    def logout(self):
        self.setCurrentWidget(self.login_window)
        self.setWindowTitle("Đăng Khoa Bank - Login")
        if self.dashboard_window:
            self.removeWidget(self.dashboard_window)
            self.dashboard_window.deleteLater()
            self.dashboard_window = None

def main():
    # Initialize Database
    init_db()

    app = QApplication(sys.argv)

    window = BankingApp()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
