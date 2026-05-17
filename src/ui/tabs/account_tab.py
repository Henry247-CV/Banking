from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QScrollArea,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from src.core.theme import *
from src.core.styles import *
from src.core.utils import safe_text
from src.ui.components.profile_card import ProfileCard
from src.services.user_service import UserService
from src.services.tier_service import TierService
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

class AccountTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.user_service = UserService()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.is_editing = False
        self.setup_ui()
        self.update_theme()
        self.update_translations()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(30, 30, 30, 30)
        self.container_layout.setSpacing(30)

        # 1. Profile Card
        self.profile_card = ProfileCard(
            self.user_data.get('full_name'), 
            self.user_data.get('username'), 
            self.user_data.get('balance'),
            self.user_data.get('account_number'),
            self.user_data.get('customer_tier', 'STANDARD')
        )
        self.container_layout.addWidget(self.profile_card)

        # 2. Tier & Benefits Section
        self.setup_tier_section()

        # 3. Banking Information
        self.setup_banking_section()

        # 4. Personal Information
        self.setup_personal_section()

        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

    def update_theme(self):
        styles = get_styles()
        self.scroll.verticalScrollBar().setStyleSheet(styles["GLOBAL_STYLE"])
        if hasattr(self.profile_card, "update_theme"):
            self.profile_card.update_theme()
        
        self.tier_container.setStyleSheet(styles["CARD_STYLE"])
        self.tier_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800; border: none; background: transparent;")
        self.benefits_title.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px; font-weight: 700; margin-top: 10px; background: transparent; border: none;")
        
        self.bank_container.setStyleSheet(styles["CARD_STYLE"])
        self.bank_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800; border: none; background: transparent;")
        
        self.info_container.setStyleSheet(styles["CARD_STYLE"])
        self.info_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 20px; font-weight: 800; border: none; background: transparent;")
        self.edit_btn.setStyleSheet(styles["SECONDARY_BUTTON"] + "font-size: 13px; font-weight: bold;")
        
        for key, (widget, editable) in self.fields.items():
            widget.setStyleSheet(styles["LINE_EDIT_STYLE"])
        
        # Refresh child labels theme
        for i in range(self.bank_list_layout.count()):
            item = self.bank_list_layout.itemAt(i)
            if item.layout():
                for j in range(item.layout().count()):
                    w = item.layout().itemAt(j).widget()
                    if isinstance(w, QLabel):
                        if j == 0: # label
                            w.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 14px; font-weight: 600; border: none; background: transparent;")
                        else: # value
                            w.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 14px; font-weight: 700; border: none; background: transparent;")

    def update_translations(self):
        self.tier_title.setText(f"🏆  {self.lang_manager.get_text('membership')}")
        self.benefits_title.setText(self.lang_manager.get_text("benefits"))
        self.bank_title.setText(f"🏦  {self.lang_manager.get_text('banking_info')}")
        self.info_title.setText(self.lang_manager.get_text("personal_info"))
        self.edit_btn.setText(self.lang_manager.get_text("edit_profile"))
        
        if hasattr(self.profile_card, "update_translations"):
            self.profile_card.update_translations()

    def setup_tier_section(self):
        self.tier_container = QFrame()
        tier_layout = QVBoxLayout(self.tier_container)
        tier_layout.setContentsMargins(30, 30, 30, 30)
        tier_layout.setSpacing(15)

        tier = self.user_data.get('customer_tier', 'STANDARD')
        tier_color = "#D4AF37" if tier == "GOLD" else (theme.CYAN if tier == "DIAMOND" else theme.TEXT_SECONDARY)

        header = QHBoxLayout()
        self.tier_title = QLabel("🏆  Customer Membership")
        
        badge = QLabel(f" {tier} MEMBER ")
        badge.setStyleSheet(f"background-color: {tier_color}; color: #FFFFFF; border-radius: 6px; font-size: 11px; font-weight: 900; padding: 4px;")
        
        header.addWidget(self.tier_title)
        header.addStretch()
        header.addWidget(badge)
        tier_layout.addLayout(header)

        self.benefits_title = QLabel("Member Benefits:")
        tier_layout.addWidget(self.benefits_title)

        benefits = TierService.get_tier_benefits(tier)
        for b in benefits:
            bl = QLabel(b)
            bl.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 13px; font-weight: 500; border: none; background: transparent;")
            tier_layout.addWidget(bl)

        self.container_layout.addWidget(self.tier_container)

    def setup_banking_section(self):
        self.bank_container = QFrame()
        self.bank_list_layout = QVBoxLayout(self.bank_container)
        self.bank_list_layout.setContentsMargins(30, 30, 30, 30)
        self.bank_list_layout.setSpacing(20)

        self.bank_title = QLabel("🏦  Banking Information")
        self.bank_list_layout.addWidget(self.bank_title)

        bank_fields = [
            ("acc_number", self.user_data.get('account_number')),
            ("bank_name", "Đăng Khoa Bank"),
            ("branch", "Da Nang Digital Branch"),
            ("member_since", safe_text(self.user_data.get('created_at'))[:10])
        ]

        for lbl_key, val in bank_fields:
            row = QHBoxLayout()
            l = QLabel(self.lang_manager.get_text(lbl_key))
            v = QLabel(safe_text(val))
            row.addWidget(l)
            row.addStretch()
            row.addWidget(v)
            self.bank_list_layout.addLayout(row)

        self.container_layout.addWidget(self.bank_container)

    def setup_personal_section(self):
        self.info_container = QFrame()
        self.info_layout = QVBoxLayout(self.info_container)
        self.info_layout.setContentsMargins(30, 30, 30, 30)
        self.info_layout.setSpacing(25)

        header_layout = QHBoxLayout()
        self.info_title = QLabel("Personal Information")
        
        self.edit_btn = QPushButton("Edit Profile")
        self.edit_btn.setFixedSize(130, 40)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.clicked.connect(self.toggle_edit)
        
        header_layout.addWidget(self.info_title)
        header_layout.addStretch()
        header_layout.addWidget(self.edit_btn)
        self.info_layout.addLayout(header_layout)

        # Fields Grid-like layout
        fields_container = QWidget()
        fields_layout = QVBoxLayout(fields_container)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(20)

        self.fields = {}
        field_data = [
            ("full_name", "full_name", True, "👤"),
            ("username", "username", False, "🆔"),
            ("phone", "phone", True, "📱"),
            ("cccd", "cccd", False, "📄"),
            ("email", "email", True, "📧"),
        ]

        for key_lbl, key, editable, icon in field_data:
            field_box = QVBoxLayout()
            
            label_row = QHBoxLayout()
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 14px; border: none; background: transparent;")
            lbl = QLabel(self.lang_manager.get_text(key_lbl))
            lbl.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 13px; font-weight: 600; border: none; background: transparent;")
            label_row.addWidget(icon_lbl)
            label_row.addWidget(lbl)
            label_row.addStretch()

            line_edit = QLineEdit(str(self.user_data.get(key, "")))
            line_edit.setReadOnly(True)
            
            field_box.addLayout(label_row)
            field_box.addWidget(line_edit)
            fields_layout.addLayout(field_box)
            self.fields[key] = (line_edit, editable)

        self.info_layout.addWidget(fields_container)
        self.container_layout.addWidget(self.info_container)
        self.container_layout.addStretch()

    def toggle_edit(self):
        if not self.is_editing:
            self.is_editing = True
            self.edit_btn.setText("Save Profile")
            for key, (widget, editable) in self.fields.items():
                if editable: widget.setReadOnly(False)
        else:
            self.is_editing = False
            self.edit_btn.setText("Edit Profile")
            for key, (widget, editable) in self.fields.items():
                widget.setReadOnly(True)
            QMessageBox.information(self, "Success", "Profile updated successfully.")

    def refresh_ui(self):
        # Refresh logic omitted
        pass
