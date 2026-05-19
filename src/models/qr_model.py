from dataclasses import dataclass
from datetime import datetime

@dataclass
class QRData:
    """Đại diện cho dữ liệu chứa trong mã QR thanh toán của Đăng Khoa Bank."""
    bank_code: str = "DKBANK"
    phone_number: str = ""
    amount: float = 0.0
    note: str = ""
    timestamp: str = ""

    def to_payload(self) -> str:
        """DKBANK|PHONE|AMOUNT|NOTE"""
        return f"{self.bank_code}|{self.phone_number}|{self.amount}|{self.note}"

    @classmethod
    def from_payload(cls, payload: str):
        parts = payload.split('|')
        if len(parts) < 2 or parts[0] != "DKBANK":
            return None
        
        return cls(
            bank_code=parts[0],
            phone_number=parts[1],
            amount=float(parts[2]) if len(parts) > 2 and parts[2] else 0.0,
            note=parts[3] if len(parts) > 3 else ""
        )
