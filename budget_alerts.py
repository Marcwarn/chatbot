"""
Budget Monitor - Track spending against budgets and send alerts
Monitors costs and sends notifications when thresholds are exceeded
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from cost_tracker import cost_tracker


class AlertLevel(Enum):
    """Alert severity levels"""
    GREEN = "green"      # Under 50% of budget
    YELLOW = "yellow"    # 50-80% of budget used
    ORANGE = "orange"    # 80-100% of budget used
    RED = "red"          # Over budget or projected to exceed


@dataclass
class BudgetStatus:
    """Current budget status"""
    current_spend: float
    budget: float
    percentage_used: float
    projected_monthly: float
    alert_level: AlertLevel
    days_into_month: int
    days_remaining: int
    daily_burn_rate: float
    recommended_daily_budget: float


@dataclass
class BudgetAlert:
    """Budget alert notification"""
    timestamp: datetime
    alert_level: AlertLevel
    threshold: float  # Percentage threshold that triggered alert
    current_spend: float
    budget: float
    message: str
    requires_action: bool


class BudgetMonitor:
    """
    Monitor spending against budgets and send alerts

    Features:
    - Set monthly/daily budgets
    - Track spending in real-time
    - Project end-of-month costs
    - Send alerts at configurable thresholds
    - Track alert history
    """

    def __init__(self, tracker=None):
        """
        Initialize budget monitor

        Args:
            tracker: CostTracker instance (uses global if None)
        """
        self.tracker = tracker or cost_tracker
        self._budgets: Dict[str, float] = {}  # period -> budget amount
        self._alert_thresholds: List[float] = [50, 80, 100]  # Default thresholds
        self._alert_history: List[BudgetAlert] = []
        self._last_alert_time: Dict[float, datetime] = {}  # threshold -> timestamp
        self._alert_callbacks: List[Callable] = []  # Functions to call on alert

    def set_budget(self, monthly_budget: float):
        """
        Set monthly budget in USD

        Args:
            monthly_budget: Budget amount in USD
        """
        self._budgets["monthly"] = monthly_budget

        # Calculate daily budget
        now = datetime.utcnow()
        days_in_month = self._get_days_in_month(now.year, now.month)
        self._budgets["daily"] = monthly_budget / days_in_month

    def set_alert_thresholds(self, thresholds: List[float]):
        """
        Set budget alert thresholds

        Args:
            thresholds: List of percentage thresholds (e.g., [50, 80, 100])
        """
        self._alert_thresholds = sorted(thresholds)

    def register_alert_callback(self, callback: Callable[[BudgetAlert], None]):
        """
        Register a callback function to be called when alert is triggered

        Args:
            callback: Function that takes BudgetAlert as parameter
        """
        self._alert_callbacks.append(callback)

    def check_budget_status(self) -> BudgetStatus:
        """
        Check current budget status

        Returns:
            BudgetStatus with current metrics
        """
        now = datetime.utcnow()
        monthly_budget = self._budgets.get("monthly", 0)

        if monthly_budget == 0:
            return BudgetStatus(
                current_spend=0.0,
                budget=0.0,
                percentage_used=0.0,
                projected_monthly=0.0,
                alert_level=AlertLevel.GREEN,
                days_into_month=now.day,
                days_remaining=self._get_days_in_month(now.year, now.month) - now.day,
                daily_burn_rate=0.0,
                recommended_daily_budget=0.0
            )

        # Get current month's spending
        current_spend = self.tracker.get_monthly_costs(now.year, now.month).get("total", 0.0)

        # Calculate metrics
        percentage_used = (current_spend / monthly_budget) * 100 if monthly_budget > 0 else 0
        days_into_month = now.day
        days_in_month = self._get_days_in_month(now.year, now.month)
        days_remaining = days_in_month - days_into_month

        # Calculate daily burn rate and projection
        daily_burn_rate = current_spend / days_into_month if days_into_month > 0 else 0
        projected_monthly = daily_burn_rate * days_in_month

        # Calculate recommended daily budget for remaining days
        remaining_budget = monthly_budget - current_spend
        recommended_daily_budget = remaining_budget / days_remaining if days_remaining > 0 else 0

        # Determine alert level
        alert_level = self._calculate_alert_level(percentage_used, projected_monthly, monthly_budget)

        return BudgetStatus(
            current_spend=round(current_spend, 2),
            budget=monthly_budget,
            percentage_used=round(percentage_used, 1),
            projected_monthly=round(projected_monthly, 2),
            alert_level=alert_level,
            days_into_month=days_into_month,
            days_remaining=days_remaining,
            daily_burn_rate=round(daily_burn_rate, 2),
            recommended_daily_budget=round(recommended_daily_budget, 2)
        )

    def send_alert_if_needed(self, force: bool = False) -> Optional[BudgetAlert]:
        """
        Check budget and send alert if threshold exceeded

        Args:
            force: Force alert even if recently sent

        Returns:
            BudgetAlert if alert was sent, None otherwise
        """
        status = self.check_budget_status()

        if status.budget == 0:
            return None  # No budget set

        # Find highest exceeded threshold
        exceeded_threshold = None
        for threshold in reversed(self._alert_thresholds):
            if status.percentage_used >= threshold:
                exceeded_threshold = threshold
                break

        if exceeded_threshold is None:
            return None  # No threshold exceeded

        # Check if we already alerted for this threshold recently (within 6 hours)
        if not force:
            last_alert = self._last_alert_time.get(exceeded_threshold)
            if last_alert and (datetime.utcnow() - last_alert) < timedelta(hours=6):
                return None  # Already alerted recently

        # Create alert
        alert = self._create_alert(status, exceeded_threshold)

        # Record alert
        self._alert_history.append(alert)
        self._last_alert_time[exceeded_threshold] = datetime.utcnow()

        # Trigger callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Alert callback error: {e}")

        return alert

    def get_alert_history(self, days: int = 30) -> List[BudgetAlert]:
        """
        Get alert history

        Args:
            days: Number of days of history to return

        Returns:
            List of BudgetAlert objects
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [
            alert for alert in self._alert_history
            if alert.timestamp >= cutoff
        ]

    def get_budget_forecast(self, days_ahead: int = 30) -> Dict:
        """
        Forecast budget status for upcoming period

        Args:
            days_ahead: Number of days to forecast

        Returns:
            Dictionary with forecast data
        """
        status = self.check_budget_status()

        # Project costs
        daily_rate = status.daily_burn_rate
        projected_costs = []

        for day in range(1, days_ahead + 1):
            projected_cost = status.current_spend + (daily_rate * day)
            date = datetime.utcnow() + timedelta(days=day)
            projected_costs.append({
                "date": date.strftime("%Y-%m-%d"),
                "projected_cost": round(projected_cost, 2),
                "budget": status.budget,
                "over_budget": projected_cost > status.budget
            })

        return {
            "current_daily_rate": status.daily_burn_rate,
            "recommended_daily_rate": status.recommended_daily_budget,
            "forecast": projected_costs,
            "projected_month_end": status.projected_monthly,
            "will_exceed_budget": status.projected_monthly > status.budget
        }

    def _calculate_alert_level(self, percentage_used: float, projected: float, budget: float) -> AlertLevel:
        """Calculate appropriate alert level"""
        # Check if projected to exceed budget
        if projected > budget * 1.1:  # Projected >110% of budget
            return AlertLevel.RED

        # Check current usage
        if percentage_used >= 100:
            return AlertLevel.RED
        elif percentage_used >= 80:
            return AlertLevel.ORANGE
        elif percentage_used >= 50:
            return AlertLevel.YELLOW
        else:
            return AlertLevel.GREEN

    def _create_alert(self, status: BudgetStatus, threshold: float) -> BudgetAlert:
        """Create alert message"""
        messages = {
            50: f"Budget Alert: You've used {status.percentage_used:.1f}% of your monthly budget (${status.current_spend:.2f}/${status.budget:.2f}). You're on track, but monitor closely.",
            80: f"Budget Warning: You've used {status.percentage_used:.1f}% of your monthly budget (${status.current_spend:.2f}/${status.budget:.2f}). Consider cost optimizations.",
            100: f"Budget Exceeded: You've used {status.percentage_used:.1f}% of your monthly budget (${status.current_spend:.2f}/${status.budget:.2f}). Take immediate action!",
        }

        # Add projection warning if needed
        message = messages.get(threshold, f"Budget alert at {threshold}%")
        if status.projected_monthly > status.budget:
            message += f" Projected month-end: ${status.projected_monthly:.2f} (${status.projected_monthly - status.budget:.2f} over budget)."

        return BudgetAlert(
            timestamp=datetime.utcnow(),
            alert_level=status.alert_level,
            threshold=threshold,
            current_spend=status.current_spend,
            budget=status.budget,
            message=message,
            requires_action=threshold >= 80
        )

    def _get_days_in_month(self, year: int, month: int) -> int:
        """Get number of days in month"""
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        current_month = datetime(year, month, 1)
        return (next_month - current_month).days

    def export_config(self) -> Dict:
        """Export budget configuration"""
        return {
            "budgets": self._budgets,
            "alert_thresholds": self._alert_thresholds,
            "alert_history": [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "alert_level": alert.alert_level.value,
                    "threshold": alert.threshold,
                    "current_spend": alert.current_spend,
                    "budget": alert.budget,
                    "message": alert.message,
                    "requires_action": alert.requires_action
                }
                for alert in self._alert_history
            ]
        }

    def import_config(self, config: Dict):
        """Import budget configuration"""
        self._budgets = config.get("budgets", {})
        self._alert_thresholds = config.get("alert_thresholds", [50, 80, 100])

        # Import alert history
        for alert_data in config.get("alert_history", []):
            alert = BudgetAlert(
                timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                alert_level=AlertLevel(alert_data["alert_level"]),
                threshold=alert_data["threshold"],
                current_spend=alert_data["current_spend"],
                budget=alert_data["budget"],
                message=alert_data["message"],
                requires_action=alert_data["requires_action"]
            )
            self._alert_history.append(alert)


# Global budget monitor instance
budget_monitor = BudgetMonitor()


# Example alert callback (can be replaced with email/Slack/etc)
def console_alert_callback(alert: BudgetAlert):
    """Print alert to console"""
    print(f"\n{'='*60}")
    print(f"🚨 BUDGET ALERT - {alert.alert_level.value.upper()}")
    print(f"{'='*60}")
    print(f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Message: {alert.message}")
    print(f"Requires Action: {'YES' if alert.requires_action else 'No'}")
    print(f"{'='*60}\n")


# Register default callback
budget_monitor.register_alert_callback(console_alert_callback)
