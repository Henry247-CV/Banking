"""
Wallet Model — Đăng Khoa Bank
Defines the wallet data structure and constants for balance management.
"""

from dataclasses import dataclass, field
from datetime import datetime


# ─── Wallet Constants ────────────────────────────────────────────────────────

DEFAULT_BALANCE = 10_000_000.0  # 10M VND default opening balance
DEFAULT_CURRENCY = "VND"


@dataclass
class Wallet:
    """Đại diện cho trạng thái ví của người dùng."""
    wallet_id: int = 0
    user_id: int = 0
    username: str = ""
    balance: float = DEFAULT_BALANCE
    currency: str = DEFAULT_CURRENCY
    account_number: str = ""
    account_status: str = "ACTIVE"
    customer_tier: str = "STANDARD"
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def is_active(self) -> bool:
        """Check if the wallet is in a usable state."""
        return self.account_status == "ACTIVE"

    def is_frozen(self) -> bool:
        return self.account_status == "FROZEN"

    def is_suspended(self) -> bool:
        return self.account_status == "SUSPENDED"

    def has_sufficient_balance(self, amount: float) -> bool:
        """Check if wallet has enough balance for a given amount."""
        return self.balance >= amount

    def to_dict(self) -> dict:
        """Convert wallet to dictionary."""
        return {
            "wallet_id": self.wallet_id,
            "user_id": self.user_id,
            "username": self.username,
            "balance": self.balance,
            "currency": self.currency,
            "account_number": self.account_number,
            "account_status": self.account_status,
            "customer_tier": self.customer_tier,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_db_row(row: dict) -> "Wallet":
        """Create a Wallet from a database row dictionary."""
        return Wallet(
            wallet_id=row.get("id", 0),
            user_id=row.get("id", 0),
            username=row.get("username", ""),
            balance=row.get("balance", DEFAULT_BALANCE),
            currency=DEFAULT_CURRENCY,
            account_number=row.get("account_number", ""),
            account_status=row.get("account_status", "ACTIVE"),
            customer_tier=row.get("customer_tier", "STANDARD"),
            updated_at=row.get("created_at", ""),
        )
