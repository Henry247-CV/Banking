"""
Savings Model — Đăng Khoa Bank
Defines the structure for savings accounts and transactions.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

class SavingsType:
    FLEXIBLE = "FLEXIBLE"
    FIXED = "FIXED"

class SavingsStatus:
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    LOCKED = "LOCKED"
    CANCELLED = "CANCELLED"

@dataclass
class SavingsAccount:
    """Represents a digital savings plan."""
    savings_id: str = field(default_factory=lambda: f"SAV-{uuid.uuid4().hex[:8].upper()}")
    username: str = ""
    plan_name: str = ""
    savings_type: str = SavingsType.FLEXIBLE
    target_amount: float = 0.0
    current_amount: float = 0.0
    interest_rate: float = 0.0
    duration_months: int = 0
    start_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_date: str = ""
    status: str = SavingsStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> dict:
        return {
            "savings_id": self.savings_id,
            "username": self.username,
            "plan_name": self.plan_name,
            "savings_type": self.savings_type,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "interest_rate": self.interest_rate,
            "duration_months": self.duration_months,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_db_row(row: dict) -> "SavingsAccount":
        return SavingsAccount(
            savings_id=row.get("savings_id", ""),
            username=row.get("username", ""),
            plan_name=row.get("plan_name", ""),
            savings_type=row.get("savings_type", SavingsType.FLEXIBLE),
            target_amount=row.get("target_amount", 0.0),
            current_amount=row.get("current_amount", 0.0),
            interest_rate=row.get("interest_rate", 0.0),
            duration_months=row.get("duration_months", 0),
            start_date=row.get("start_date", ""),
            end_date=row.get("end_date", ""),
            status=row.get("status", SavingsStatus.ACTIVE),
            created_at=row.get("created_at", ""),
        )

@dataclass
class SavingsTransaction:
    """Đại diện cho một giao dịch trong tài khoản tiết kiệm."""
    id: int = 0
    savings_id: str = ""
    amount: float = 0.0
    transaction_type: str = "DEPOSIT" # DEPOSIT, WITHDRAWAL, INTEREST
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
