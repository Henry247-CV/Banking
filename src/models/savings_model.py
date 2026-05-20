from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SavingsAccount:
    id: Optional[int]
    username: str
    plan_name: str
    savings_type: str  # 'FLEXIBLE' or 'FIXED'
    target_amount: float
    current_amount: float
    interest_rate: float
    duration_months: int
    start_date: str
    end_date: Optional[str]
    status: str  # 'ACTIVE', 'COMPLETED', 'LOCKED', 'CANCELLED'
    created_at: str
    interest_earned: float = 0.0
    last_growth_update: str = ""

    @classmethod
    def from_db_row(cls, row):
        """Resiliently create a SavingsAccount from a database row (dict or sqlite3.Row)."""
        data = dict(row)
        # Handle schema mismatch: map 'savings_id' to 'id' if 'id' is missing
        if 'id' not in data and 'savings_id' in data:
            data['id'] = data.pop('savings_id')
        
        # Filter out any keys that are not fields in the dataclass
        import inspect
        fields = inspect.signature(cls).parameters
        filtered_data = {k: v for k, v in data.items() if k in fields}
        return cls(**filtered_data)

    @property
    def progress(self) -> float:
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, (self.current_amount / self.target_amount) * 100)

@dataclass
class SavingsTransaction:
    id: Optional[int]
    savings_id: int
    username: str
    type: str  # 'DEPOSIT', 'WITHDRAWAL', 'INTEREST'
    amount: float
    created_at: str
