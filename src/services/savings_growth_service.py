from datetime import datetime, timedelta
from src.services.savings_service import SavingsService

class SavingsGrowthService:
    @staticmethod
    def calculate_interest_growth(username):
        """Calculates and applies interest growth for all active plans of a user."""
        savings = SavingsService.get_user_savings(username)
        applied_any = False
        
        for plan in savings:
            if plan.status != 'ACTIVE':
                continue
                
            # Parse last update time
            try:
                # Fallback to created_at if last_growth_update is missing
                last_upd_str = plan.last_growth_update or plan.created_at
                last_upd = datetime.strptime(last_upd_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Handle potential date format issues
                last_upd = datetime.now() - timedelta(seconds=10)
            
            elapsed = (datetime.now() - last_upd).total_seconds()
            
            # Minimum update interval: 5 seconds to prevent sqlite spam
            if elapsed < 5:
                continue
                
            # Interest Formula (Incremental for the elapsed seconds)
            # Annual Interest / (Seconds in Year) * Seconds Elapsed
            seconds_in_year = 365 * 24 * 3600
            interest_increment = (plan.current_amount * plan.interest_rate / seconds_in_year) * elapsed
            
            if interest_increment > 0.01: # Only apply if > 0.01 VND
                SavingsService.add_interest_growth(plan.id, interest_increment)
                applied_any = True
                
        return applied_any

    @staticmethod
    def get_live_stats(username):
        """Returns refreshed statistics, potentially triggering a growth calculation."""
        # Optional: trigger calculation when stats are requested
        # SavingsGrowthService.calculate_interest_growth(username)
        return SavingsService.get_savings_stats(username)
