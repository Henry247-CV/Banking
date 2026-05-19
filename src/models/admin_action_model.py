from dataclasses import dataclass
from datetime import datetime

class AdminActionType:
    USER_SUSPENDED = "USER_SUSPENDED"
    USER_ACTIVATED = "USER_ACTIVATED"
    USER_LOCKED = "USER_LOCKED"
    USER_UNLOCKED = "USER_UNLOCKED"
    WALLET_FROZEN = "WALLET_FROZEN"
    WALLET_UNFROZEN = "WALLET_UNFROZEN"
    TIER_UPDATED = "TIER_UPDATED"
    VERIFICATION_STATUS_UPDATED = "VERIFICATION_STATUS_UPDATED"
    BALANCE_ADJUSTED = "BALANCE_ADJUSTED"
    PROFILE_UPDATED = "PROFILE_UPDATED"

@dataclass
class AdminAction:
    """Đại diện cho một hành động quản trị viên thực hiện trên hệ thống."""
    admin_username: str
    action_type: str
    target_username: str
    details: str
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_db_row(self):
        return (self.admin_username, self.action_type, self.target_username, self.details, self.timestamp)
