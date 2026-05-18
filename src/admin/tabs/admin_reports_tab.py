from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import src.core.theme as theme
from src.core.language_manager import LanguageManager
from src.core.theme_manager import ThemeManager

from src.admin.components.coming_soon_card import ComingSoonCard
from src.admin.components.report_preview_card import ReportPreviewCard

class AdminReportsTab(QWidget):
    """Admin Report Center — A premium placeholder for future reporting modules."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.theme_manager = ThemeManager()
        self.setObjectName("AdminReportsTab")
        self._setup_ui()
        self.update_theme()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setObjectName("AdminReportsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("AdminReportsContent")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(28, 24, 28, 24)
        self.main_layout.setSpacing(32)

        # ── Header ──
        self._build_header()

        # ── Report Previews ──
        self._build_report_previews()

        # ── Export & Integrations Previews ──
        self._build_export_previews()

        # ── Future Roadmap ──
        self._build_future_roadmap()

        self.main_layout.addStretch()
        scroll.setWidget(content)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _build_header(self):
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        self.header_title = QLabel(self.lang_manager.get_text("admin_reports_header_title"))
        self.header_title.setObjectName("AdminReportsHeaderTitle")
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        self.header_title.setFont(title_font)
        
        self.header_desc = QLabel(self.lang_manager.get_text("admin_reports_header_desc"))
        self.header_desc.setObjectName("AdminReportsHeaderDesc")
        self.header_desc.setFont(QFont("Segoe UI", 12))
        self.header_desc.setWordWrap(True)

        header_layout.addWidget(self.header_title)
        header_layout.addWidget(self.header_desc)
        self.main_layout.addLayout(header_layout)

        # Hero Coming Soon Card
        self.hero_card = QFrame()
        self.hero_card.setObjectName("AdminReportsHeroCard")
        hero_layout = QHBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(24, 20, 24, 20)
        
        hero_info = QVBoxLayout()
        self.hero_title = QLabel("COMING SOON")
        self.hero_title.setObjectName("AdminReportsHeroTitle")
        self.hero_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        
        self.hero_desc = QLabel(self.lang_manager.get_text("admin_reports_hero_desc"))
        self.hero_desc.setObjectName("AdminReportsHeroDesc")
        self.hero_desc.setFont(QFont("Segoe UI", 11))
        
        hero_info.addWidget(self.hero_title)
        hero_info.addWidget(self.hero_desc)
        
        hero_layout.addLayout(hero_info)
        hero_layout.addStretch()
        
        icon_lbl = QLabel("🚧")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 32))
        hero_layout.addWidget(icon_lbl)
        
        self.main_layout.addWidget(self.hero_card)

    def _build_report_previews(self):
        self.preview_section_title = QLabel(self.lang_manager.get_text("admin_report_modules"))
        self.preview_section_title.setObjectName("AdminReportsSectionTitle")
        self.main_layout.addWidget(self.preview_section_title)

        grid = QGridLayout()
        grid.setSpacing(16)

        self.cards_preview = [
            ReportPreviewCard(
                title=self.lang_manager.get_text("admin_rep_txn_title"),
                description=self.lang_manager.get_text("admin_rep_txn_desc"),
                status="IN DEVELOPMENT", icon="💳"
            ),
            ReportPreviewCard(
                title=self.lang_manager.get_text("admin_rep_cust_title"),
                description=self.lang_manager.get_text("admin_rep_cust_desc"),
                status="PLANNED", icon="👥"
            ),
            ReportPreviewCard(
                title=self.lang_manager.get_text("admin_rep_fraud_title"),
                description=self.lang_manager.get_text("admin_rep_fraud_desc"),
                status="ENTERPRISE", icon="🛡️"
            ),
            ReportPreviewCard(
                title=self.lang_manager.get_text("admin_rep_finance_title"),
                description=self.lang_manager.get_text("admin_rep_finance_desc"),
                status="PLANNED", icon="📈"
            )
        ]

        # translation keys for cards
        self._preview_keys = [
            ("admin_rep_txn_title", "admin_rep_txn_desc", "admin_status_in_dev"),
            ("admin_rep_cust_title", "admin_rep_cust_desc", "admin_status_planned"),
            ("admin_rep_fraud_title", "admin_rep_fraud_desc", "admin_status_enterprise"),
            ("admin_rep_finance_title", "admin_rep_finance_desc", "admin_status_planned")
        ]

        grid.addWidget(self.cards_preview[0], 0, 0)
        grid.addWidget(self.cards_preview[1], 0, 1)
        grid.addWidget(self.cards_preview[2], 1, 0)
        grid.addWidget(self.cards_preview[3], 1, 1)
        
        self.main_layout.addLayout(grid)

    def _build_export_previews(self):
        self.export_section_title = QLabel(self.lang_manager.get_text("admin_export_options"))
        self.export_section_title.setObjectName("AdminReportsSectionTitle")
        self.main_layout.addWidget(self.export_section_title)

        export_layout = QHBoxLayout()
        export_layout.setSpacing(16)

        self.export_btns = []
        btn_data = [
            ("admin_btn_export_pdf", "📄"),
            ("admin_btn_export_excel", "📊"),
            ("admin_btn_generate_report", "⚡"),
            ("admin_btn_schedule_report", "⏱️")
        ]

        for key, icon in btn_data:
            btn = QPushButton(f"{icon}  {self.lang_manager.get_text(key)}")
            btn.setObjectName("AdminExportPreviewBtn")
            btn.setFixedHeight(42)
            btn.setEnabled(False)
            btn.setToolTip(self.lang_manager.get_text("admin_feature_future"))
            export_layout.addWidget(btn)
            self.export_btns.append((btn, key, icon))

        self.main_layout.addLayout(export_layout)

    def _build_future_roadmap(self):
        self.roadmap_section_title = QLabel(self.lang_manager.get_text("admin_future_roadmap"))
        self.roadmap_section_title.setObjectName("AdminReportsSectionTitle")
        self.main_layout.addWidget(self.roadmap_section_title)

        grid = QGridLayout()
        grid.setSpacing(16)

        self.cards_roadmap = [
            ComingSoonCard(
                title=self.lang_manager.get_text("admin_rdmp_ai_title"),
                description=self.lang_manager.get_text("admin_rdmp_ai_desc"),
                icon="🤖"
            ),
            ComingSoonCard(
                title=self.lang_manager.get_text("admin_rdmp_auto_title"),
                description=self.lang_manager.get_text("admin_rdmp_auto_desc"),
                icon="⚙️"
            ),
            ComingSoonCard(
                title=self.lang_manager.get_text("admin_rdmp_smart_title"),
                description=self.lang_manager.get_text("admin_rdmp_smart_desc"),
                icon="🧠"
            ),
            ComingSoonCard(
                title=self.lang_manager.get_text("admin_rdmp_cloud_title"),
                description=self.lang_manager.get_text("admin_rdmp_cloud_desc"),
                icon="☁️"
            )
        ]

        self._roadmap_keys = [
            ("admin_rdmp_ai_title", "admin_rdmp_ai_desc"),
            ("admin_rdmp_auto_title", "admin_rdmp_auto_desc"),
            ("admin_rdmp_smart_title", "admin_rdmp_smart_desc"),
            ("admin_rdmp_cloud_title", "admin_rdmp_cloud_desc")
        ]

        grid.addWidget(self.cards_roadmap[0], 0, 0)
        grid.addWidget(self.cards_roadmap[1], 0, 1)
        grid.addWidget(self.cards_roadmap[2], 1, 0)
        grid.addWidget(self.cards_roadmap[3], 1, 1)

        self.main_layout.addLayout(grid)

    def update_translations(self):
        # Headers
        self.header_title.setText(self.lang_manager.get_text("admin_reports_header_title"))
        self.header_desc.setText(self.lang_manager.get_text("admin_reports_header_desc"))
        self.hero_desc.setText(self.lang_manager.get_text("admin_reports_hero_desc"))
        
        # Section Titles
        self.preview_section_title.setText(self.lang_manager.get_text("admin_report_modules"))
        self.export_section_title.setText(self.lang_manager.get_text("admin_export_options"))
        self.roadmap_section_title.setText(self.lang_manager.get_text("admin_future_roadmap"))

        # Preview Cards
        for i, card in enumerate(self.cards_preview):
            t_key, d_key, s_key = self._preview_keys[i]
            card.update_translations(self.lang_manager, t_key, d_key, s_key)

        # Export Buttons
        for btn, key, icon in self.export_btns:
            btn.setText(f"{icon}  {self.lang_manager.get_text(key)}")
            btn.setToolTip(self.lang_manager.get_text("admin_feature_future"))

        # Roadmap Cards
        for i, card in enumerate(self.cards_roadmap):
            t_key, d_key = self._roadmap_keys[i]
            card.update_translations(self.lang_manager, t_key, d_key)

    def update_theme(self):
        theme.update_globals()
        
        self.setStyleSheet(f"background-color: {theme.BACKGROUND};")

        self.header_title.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; background: transparent; border: none;")
        self.header_desc.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; background: transparent; border: none;")

        self.hero_card.setStyleSheet(f"""
            QFrame#AdminReportsHeroCard {{
                background-color: {theme.PANEL_BG};
                border: 1px solid {theme.BORDER};
                border-left: 6px solid {theme.CYAN};
                border-radius: 12px;
            }}
        """)
        self.hero_title.setStyleSheet(f"color: {theme.CYAN}; background: transparent; border: none;")
        self.hero_desc.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; background: transparent; border: none;")

        section_title_style = f"""
            color: {theme.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 800;
            background: transparent;
            border: none;
            padding-bottom: 4px;
        """
        self.preview_section_title.setStyleSheet(section_title_style)
        self.export_section_title.setStyleSheet(section_title_style)
        self.roadmap_section_title.setStyleSheet(section_title_style)

        for btn, _, _ in self.export_btns:
            btn.setStyleSheet(f"""
                QPushButton#AdminExportPreviewBtn {{
                    background-color: {theme.PANEL_BG};
                    color: {theme.TEXT_SECONDARY};
                    border: 1px dashed {theme.BORDER};
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }}
            """)

        for card in self.cards_preview:
            card.update_theme()
        
        for card in self.cards_roadmap:
            card.update_theme()

    def update_ui(self):
        """Called when tab is shown."""
        self.update_theme()
        self.update_translations()