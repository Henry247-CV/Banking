"""
Transaction Model — Đăng Khoa Bank
Defines the transaction data structure, statuses, and types.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ─── Transaction Statuses ────────────────────────────────────────────────────

class TransactionStatus:
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    ROLLED_BACK = "ROLLED_BACK"

    ALL = [SUCCESS, FAILED, PENDING, ROLLED_BACK]


# ─── Transaction Types ────────────────────────────────────────────────────────

class TransactionType:
    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"
    QR_TRANSFER = "QR_TRANSFER"
    ADMIN_ADJUSTMENT = "ADMIN_ADJUSTMENT"

    ALL = [TRANSFER, DEPOSIT, WITHDRAWAL, REFUND, QR_TRANSFER, ADMIN_ADJUSTMENT]


@dataclass
class Transaction:
    """Đại diện cho một giao dịch ngân hàng đơn lẻ."""
    transaction_id: str = field(default_factory=lambda: f"TXN-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}")
    sender_username: str = ""
    receiver_bank: str = ""
    receiver_account: str = ""
    amount: float = 0.0
    status: str = TransactionStatus.PENDING
    transaction_type: str = TransactionType.TRANSFER
    note: str = ""
    flagged: int = 0
    risk_level: str = "LOW"
    review_status: str = "COMPLETED"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def is_success(self) -> bool:
        return self.status == TransactionStatus.SUCCESS

    def is_failed(self) -> bool:
        return self.status == TransactionStatus.FAILED

    def is_rolled_back(self) -> bool:
        return self.status == TransactionStatus.ROLLED_BACK

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "sender_username": self.sender_username,
            "receiver_bank": self.receiver_bank,
            "receiver_account": self.receiver_account,
            "amount": self.amount,
            "status": self.status,
            "transaction_type": self.transaction_type,
            "note": self.note,
            "flagged": self.flagged,
            "risk_level": self.risk_level,
            "review_status": self.review_status,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_db_row(row: dict) -> "Transaction":
        """Create a Transaction from a database row dictionary."""
        return Transaction(
            transaction_id=str(row.get("transaction_id", row.get("id", ""))),
            sender_username=row.get("sender_username", ""),
            receiver_bank=row.get("receiver_bank", ""),
            receiver_account=row.get("receiver_account", ""),
            amount=row.get("amount", 0.0),
            status=row.get("status", TransactionStatus.PENDING),
            transaction_type=row.get("transaction_type", TransactionType.TRANSFER),
            note=row.get("note", ""),
            flagged=row.get("flagged", 0),
            risk_level=row.get("risk_level", "LOW"),
            review_status=row.get("review_status", "COMPLETED"),
            created_at=row.get("created_at", ""),
        )
