from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import src.core.theme as theme

class BackupCard(QFrame):
    """Card displaying current backup status and actions."""
    create_requested = pyqtSignal()
    restore_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()

    def __init__(self, last_backup="Never", db_size="0 MB", count=0):
        super().__init__()
        self.setObjectName("BackupCard")
        self.last_backup = last_backup
        self.db_size = db_size
        self.count = count
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        icon = QLabel("💾")
        icon.setFixedSize(32, 32)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 16))
        
        self.title_lbl = QLabel("Local SQLite Backup")
        title_font = QFont("Segoe UI", 12)
        title_font.setBold(True)
        self.title_lbl.setFont(title_font)
        
        header_row.addWidget(icon)
        header_row.addWidget(self.title_lbl)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Info
        info_layout = QHBoxLayout()
        info_layout.setSpacing(24)

        self.last_lbl = self._create_info_block("Last Backup", self.last_backup)
        self.size_lbl = self._create_info_block("Database Size", self.db_size)
        self.count_lbl = self._create_info_block("Backup Count", str(self.count))

        info_layout.addWidget(self.last_lbl)
        info_layout.addWidget(self.size_lbl)
        info_layout.addWidget(self.count_lbl)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        self.btn_create = QPushButton("Create Backup")
        self.btn_create.setObjectName("BackupBtnCreate")
        self.btn_create.setFixedHeight(36)
        self.btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create.clicked.connect(self.create_requested.emit)

        self.btn_restore = QPushButton("Restore Backup")
        self.btn_restore.setObjectName("BackupBtnRestore")
        self.btn_restore.setFixedHeight(36)
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.clicked.connect(self.restore_requested.emit)

        self.btn_folder = QPushButton("Open Backup Folder")
        self.btn_folder.setObjectName("BackupBtnFolder")
        self.btn_folder.setFixedHeight(36)
        self.btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_folder.clicked.connect(self.open_folder_requested.emit)

        actions_row.addWidget(self.btn_create)
        actions_row.addWidget(self.btn_restore)
        actions_row.addStretch()
        actions_row.addWidget(self.btn_folder)

        layout.addLayout(actions_row)

    def _create_info_block(self, title, val):
        container = QWidget()
        l = QVBoxLayout(container)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)
        
        lbl_t = QLabel(title)
        lbl_t.setObjectName("BackupInfoTitle")
        lbl_t.setFont(QFont("Segoe UI", 10))
        
        lbl_v = QLabel(val)
        lbl_v.setObjectName("BackupInfoVal")
        lbl_v.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        l.addWidget(lbl_t)
        l.addWidget(lbl_v)
        return container

    def update_data(self, last_backup, db_size, count):
        # Update the value labels inside the containers
        self.last_lbl.layout().itemAt(1).widget().setText(last_backup)
        self.size_lbl.layout().itemAt(1).widget().setText(db_size)
        self.count_lbl.layout().itemAt(1).widget().setText(str(count))

    def update_translations(self, lang_manager):
        self.title_lbl.setText(lang_manager.get_text("admin_backup_title"))
        self.btn_create.setText(lang_manager.get_text("admin_btn_create_backup"))
        self.btn_restore.setText(lang_manager.get_text("admin_btn_restore_backup"))
        self.btn_folder.setText(lang_manager.get_text("admin_btn_open_folder"))
        
        self.last_lbl.layout().itemAt(0).widget().setText(lang_manager.get_text("admin_last_backup"))
        self.size_lbl.layout().itemAt(0).widget().setText(lang_manager.get_text("admin_db_size"))
        self.count_lbl.layout().itemAt(0).widget().setText(lang_manager.get_text("admin_backup_count"))

    def update_theme(self):
        theme.update_globals()
        
        self.setStyleSheet(f"""
            QFrame#BackupCard {{
                background-color: {theme.CARD_BG};
                border: 1px solid {theme.BORDER};
                border-left: 4px solid {theme.CYAN};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {theme.TEXT_PRIMARY};
            }}
            QLabel#BackupInfoTitle {{
                color: {theme.TEXT_SECONDARY};
            }}
            QLabel#BackupInfoVal {{
                color: {theme.CYAN};
            }}
            QPushButton#BackupBtnCreate {{
                background-color: {theme.CYAN};
                color: {theme.BACKGROUND};
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-weight: bold;
            }}
            QPushButton#BackupBtnCreate:hover {{
                background-color: {theme.CYAN_HOVER};
            }}
            QPushButton#BackupBtnRestore {{
                background-color: {theme.RED}20;
                color: {theme.RED};
                border: 1px solid {theme.RED}40;
                border-radius: 6px;
                padding: 0 16px;
                font-weight: bold;
            }}
            QPushButton#BackupBtnRestore:hover {{
                background-color: {theme.RED};
                color: white;
            }}
            QPushButton#BackupBtnFolder {{
                background-color: {theme.PANEL_BG};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 0 16px;
                font-weight: bold;
            }}
            QPushButton#BackupBtnFolder:hover {{
                border-color: {theme.CYAN};
                color: {theme.CYAN};
            }}
        """)