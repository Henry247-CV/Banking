"""
Dịch vụ Biên lai — Đăng Khoa Bank
Xử lý định dạng dữ liệu biên lai và logic xuất hình ảnh.
"""

import os
from datetime import datetime
from pathlib import Path
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget


class ReceiptService:
    """Dịch vụ quản lý biên lai chuyển khoản và xuất hóa đơn."""

    @staticmethod
    def get_desktop_path() -> Path:
        """Trả về đường dẫn màn hình chính (Desktop) của người dùng."""
        return Path.home() / "Desktop"

    @staticmethod
    def generate_receipt_filename(transaction_id: str) -> str:
        """Tạo tên tệp duy nhất cho hình ảnh biên lai."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize transaction_id for filename
        safe_id = transaction_id.replace("-", "_")
        return f"DKB_Receipt_{safe_id}_{timestamp}.png"

    @staticmethod
    def save_widget_as_image(widget: QWidget, transaction_id: str) -> tuple[bool, str]:
        """
        Chụp một QWidget dưới dạng QPixmap và lưu nó vào Desktop.
        Trả về (thành công, thông báo/đường dẫn).
        """
        try:
            # Chụp widget
            pixmap = widget.grab()
            
            # Chuẩn bị đường dẫn
            desktop = ReceiptService.get_desktop_path()
            filename = ReceiptService.generate_receipt_filename(transaction_id)
            save_path = desktop / filename
            
            # Lưu pixmap
            if pixmap.save(str(save_path), "PNG"):
                return True, str(save_path)
            else:
                return False, "Không thể lưu tệp hình ảnh."
        except Exception as e:
            return False, f"Lỗi xuất file: {str(e)}"

    @staticmethod
    def format_amount(amount: float) -> str:
        """Định dạng tiền tệ để hiển thị trên biên lai."""
        return f"{amount:,.0f} VND"

    @staticmethod
    def format_date(date_str: str) -> str:
        """Định dạng ngày giao dịch để hiển thị tốt hơn."""
        try:
            # Giả sử đầu vào là YYYY-MM-DD HH:MM:SS
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d %b %Y, %H:%M")
        except Exception:
            return date_str
