"""
Cost Analytics - Advanced cost analysis and forecasting
Provides deep insights into cost patterns, ROI, and predictions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics
from cost_tracker import cost_tracker, FeatureType, ServiceType


@dataclass
class CostAnomaly:
    """Detected cost anomaly"""
    timestamp: datetime
    anomaly_type: str  # "spike", "unusual_pattern", "potential_abuse"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    current_value: float
    expected_value: float
    deviation_percentage: float
    suggested_actions: List[str]


class CostAnalytics:
    """
    Advanced cost analytics and forecasting

    Features:
    - Cost per user/assessment calculations
    - ROI analysis
    - Anomaly detection with statistical methods
    - Cost forecasting with trend analysis
    - Feature profitability analysis
    """

    def __init__(self, tracker=None):
        """
        Initialize cost analytics

        Args:
            tracker: CostTracker instance (uses global if None)
        """
        self.tracker = tracker or cost_tracker

    def calculate_cost_per_user(self, days: int = 30) -> Dict:
        """
        Calculate average cost per user

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with cost per user metrics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get all calls with user_id
        calls_with_users = [
            c for c in self.tracker._calls
            if c.timestamp >= cutoff and c.user_id
        ]

        if not calls_with_users:
            return {
                "total_users": 0,
                "total_cost": 0.0,
                "avg_cost_per_user": 0.0,
                "median_cost_per_user": 0.0,
                "max_cost_user": None
            }

        # Group by user
        user_costs = {}
        for call in calls_with_users:
            user_id = call.user_id
            user_costs[user_id] = user_costs.get(user_id, 0.0) + call.cost

        costs = list(user_costs.values())
        total_cost = sum(costs)

        # Find max cost user
        max_user = max(user_costs.items(), key=lambda x: x[1])

        return {
            "total_users": len(user_costs),
            "total_cost": round(total_cost, 2),
            "avg_cost_per_user": round(total_cost / len(user_costs), 4),
            "median_cost_per_user": round(statistics.median(costs), 4),
            "max_cost_user": {
                "user_id": max_user[0],
                "cost": round(max_user[1], 2)
            },
            "cost_distribution": {
                "min": round(min(costs), 4),
                "25th_percentile": round(statistics.quantiles(costs, n=4)[0], 4) if len(costs) > 1 else 0,
                "75th_percentile": round(statistics.quantiles(costs, n=4)[2], 4) if len(costs) > 1 else 0,
                "max": round(max(costs), 4)
            }
        }

    def calculate_cost_per_assessment(self, days: int = 30) -> Dict:
        """
        Calculate detailed cost metrics per assessment

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with assessment cost metrics
        """
        assessment_costs = self.tracker.get_average_cost_per_assessment(days)

        if assessment_costs["total_assessments"] == 0:
            return {
                **assessment_costs,
                "cost_breakdown": {},
                "efficiency_metrics": {}
            }

        # Get feature breakdown for assessments
        cutoff = datetime.utcnow() - timedelta(days=days)
        assessment_calls = [
            c for c in self.tracker._calls
            if c.timestamp >= cutoff and c.assessment_id
        ]

        # Breakdown by feature
        feature_costs = {}
        for call in assessment_calls:
            feature = call.feature.value
            feature_costs[feature] = feature_costs.get(feature, 0.0) + call.cost

        return {
            **assessment_costs,
            "cost_breakdown": feature_costs,
            "efficiency_metrics": {
                "reports_per_dollar": round(1 / assessment_costs["avg_cost_per_assessment"], 2) if assessment_costs["avg_cost_per_assessment"] > 0 else 0,
                "target_cost": 0.10,  # Target $0.10 per assessment
                "vs_target": "above" if assessment_costs["avg_cost_per_assessment"] > 0.10 else "below"
            }
        }

    def calculate_roi(self, revenue_per_assessment: Optional[float] = None) -> Dict:
        """
        Calculate return on investment metrics

        Args:
            revenue_per_assessment: Revenue per completed assessment (if monetized)

        Returns:
            Dictionary with ROI metrics
        """
        cost_metrics = self.calculate_cost_per_assessment(30)

        if cost_metrics["total_assessments"] == 0:
            return {
                "status": "no_data",
                "message": "No assessment data available"
            }

        cost_per_assessment = cost_metrics["avg_cost_per_assessment"]

        roi_data = {
            "cost_per_assessment": cost_per_assessment,
            "assessments_per_month": cost_metrics["total_assessments"],
            "monthly_cost": cost_metrics["total_cost"]
        }

        if revenue_per_assessment:
            profit_per_assessment = revenue_per_assessment - cost_per_assessment
            monthly_revenue = revenue_per_assessment * cost_metrics["total_assessments"]
            monthly_profit = monthly_revenue - cost_metrics["total_cost"]

            roi_percentage = (monthly_profit / cost_metrics["total_cost"]) * 100 if cost_metrics["total_cost"] > 0 else 0

            roi_data.update({
                "revenue_per_assessment": revenue_per_assessment,
                "profit_per_assessment": round(profit_per_assessment, 4),
                "profit_margin": round((profit_per_assessment / revenue_per_assessment) * 100, 1) if revenue_per_assessment > 0 else 0,
                "monthly_revenue": round(monthly_revenue, 2),
                "monthly_profit": round(monthly_profit, 2),
                "roi_percentage": round(roi_percentage, 1),
                "break_even_assessments": round(cost_metrics["total_cost"] / revenue_per_assessment) if revenue_per_assessment > 0 else 0
            })

        return roi_data

    def identify_cost_anomalies(self, days: int = 30, sensitivity: float = 2.0) -> List[CostAnomaly]:
        """
        Detect cost anomalies using statistical methods

        Args:
            days: Number of days to analyze
            sensitivity: Standard deviations for anomaly detection (default: 2.0)

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Get daily cost trends
        trends = self.tracker.get_cost_trends(days)
        if len(trends) < 7:
            return anomalies  # Need at least a week of data

        daily_costs = [t["total"] for t in trends]

        # Calculate statistics
        mean_cost = statistics.mean(daily_costs)
        stdev_cost = statistics.stdev(daily_costs) if len(daily_costs) > 1 else 0

        # Detect spikes (outliers)
        threshold = mean_cost + (sensitivity * stdev_cost)

        for i, trend in enumerate(trends):
            if trend["total"] > threshold:
                deviation = ((trend["total"] - mean_cost) / mean_cost) * 100 if mean_cost > 0 else 0

                anomalies.append(CostAnomaly(
                    timestamp=datetime.strptime(trend["date"], "%Y-%m-%d"),
                    anomaly_type="spike",
                    severity="high" if deviation > 200 else "medium",
                    description=f"Cost spike detected on {trend['date']}",
                    current_value=trend["total"],
                    expected_value=mean_cost,
                    deviation_percentage=deviation,
                    suggested_actions=[
                        "Review API calls for this date",
                        "Check for unusual user activity",
                        "Verify no duplicate report generations",
                        "Check for potential API abuse"
                    ]
                ))

        # Detect unusual patterns (e.g., consistent increase)
        if len(daily_costs) >= 7:
            recent_avg = statistics.mean(daily_costs[-7:])
            earlier_avg = statistics.mean(daily_costs[:7])

            if recent_avg > earlier_avg * 1.5:  # 50% increase
                anomalies.append(CostAnomaly(
                    timestamp=datetime.utcnow(),
                    anomaly_type="unusual_pattern",
                    severity="medium",
                    description="Sustained cost increase detected",
                    current_value=recent_avg,
                    expected_value=earlier_avg,
                    deviation_percentage=((recent_avg - earlier_avg) / earlier_avg) * 100,
                    suggested_actions=[
                        "Analyze recent feature changes",
                        "Check for increased user activity",
                        "Review cache hit rates",
                        "Verify prompt efficiency"
                    ]
                ))

        # Detect potential abuse (same user generating excessive requests)
        user_metrics = self.calculate_cost_per_user(days)
        if user_metrics["total_users"] > 0:
            max_user_cost = user_metrics["max_cost_user"]["cost"]
            avg_user_cost = user_metrics["avg_cost_per_user"]

            if max_user_cost > avg_user_cost * 10:  # 10x average
                anomalies.append(CostAnomaly(
                    timestamp=datetime.utcnow(),
                    anomaly_type="potential_abuse",
                    severity="high",
                    description=f"User {user_metrics['max_cost_user']['user_id']} has unusually high costs",
                    current_value=max_user_cost,
                    expected_value=avg_user_cost,
                    deviation_percentage=((max_user_cost - avg_user_cost) / avg_user_cost) * 100,
                    suggested_actions=[
                        f"Investigate user {user_metrics['max_cost_user']['user_id']}",
                        "Check for automated/bot activity",
                        "Review rate limiting settings",
                        "Consider implementing per-user quotas"
                    ]
                ))

        return anomalies

    def forecast_costs(self, days_ahead: int = 30, method: str = "linear") -> Dict:
        """
        Forecast future costs based on historical trends

        Args:
            days_ahead: Number of days to forecast
            method: Forecasting method ("linear", "moving_average")

        Returns:
            Dictionary with forecast data
        """
        # Get historical data
        historical_days = min(days_ahead * 2, 60)  # Use 2x forecast period or max 60 days
        trends = self.tracker.get_cost_trends(historical_days)

        if len(trends) < 7:
            return {
                "status": "insufficient_data",
                "message": "Need at least 7 days of data for forecasting"
            }

        daily_costs = [t["total"] for t in trends]
        dates = [datetime.strptime(t["date"], "%Y-%m-%d") for t in trends]

        # Calculate trend
        if method == "linear":
            forecast = self._linear_forecast(daily_costs, days_ahead)
        else:  # moving_average
            forecast = self._moving_average_forecast(daily_costs, days_ahead)

        # Generate forecast dates
        last_date = dates[-1]
        forecast_data = []

        for i, cost in enumerate(forecast, 1):
            forecast_date = last_date + timedelta(days=i)
            forecast_data.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "forecasted_cost": round(cost, 2)
            })

        # Calculate monthly projection
        total_forecast = sum(forecast)
        current_month_cost = self.tracker.get_monthly_costs().get("total", 0)

        return {
            "status": "success",
            "method": method,
            "historical_days": len(trends),
            "forecast_days": days_ahead,
            "current_daily_avg": round(statistics.mean(daily_costs), 2),
            "forecasted_daily_avg": round(sum(forecast) / len(forecast), 2),
            "current_month_cost": round(current_month_cost, 2),
            "projected_month_end": round(current_month_cost + total_forecast, 2),
            "forecast": forecast_data,
            "confidence": "medium" if len(trends) >= 30 else "low"
        }

    def get_feature_profitability(self, days: int = 30) -> Dict:
        """
        Analyze profitability of each feature

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with feature profitability metrics
        """
        cost_breakdown = self.tracker.get_cost_breakdown_by_feature(days)

        # Calculate total
        total_cost = sum(cost_breakdown.values())

        # Calculate percentages and costs
        features = []
        for feature, cost in cost_breakdown.items():
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            features.append({
                "feature": feature,
                "cost": round(cost, 2),
                "percentage": round(percentage, 1),
                "monthly_projection": round(cost * (30 / days), 2)
            })

        # Sort by cost descending
        features.sort(key=lambda x: x["cost"], reverse=True)

        return {
            "period_days": days,
            "total_cost": round(total_cost, 2),
            "features": features,
            "top_cost_driver": features[0]["feature"] if features else None
        }

    def _linear_forecast(self, data: List[float], days_ahead: int) -> List[float]:
        """Simple linear regression forecast"""
        n = len(data)
        x = list(range(n))
        y = data

        # Calculate slope and intercept
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            # No trend, use average
            avg = y_mean
            return [avg] * days_ahead

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Generate forecast
        forecast = []
        for i in range(n, n + days_ahead):
            forecast.append(max(0, slope * i + intercept))  # Don't predict negative costs

        return forecast

    def _moving_average_forecast(self, data: List[float], days_ahead: int, window: int = 7) -> List[float]:
        """Moving average forecast"""
        # Use last 'window' days for forecast
        recent = data[-window:]
        avg = statistics.mean(recent)

        # Simple projection: use moving average
        return [avg] * days_ahead

    def generate_comprehensive_report(self, days: int = 30) -> Dict:
        """
        Generate comprehensive cost analytics report

        Args:
            days: Number of days to analyze

        Returns:
            Complete analytics report
        """
        return {
            "report_date": datetime.utcnow().isoformat(),
            "analysis_period_days": days,
            "overview": {
                "total_cost": self.tracker.get_monthly_costs().get("total", 0),
                "daily_costs": self.tracker.get_daily_costs()
            },
            "cost_per_user": self.calculate_cost_per_user(days),
            "cost_per_assessment": self.calculate_cost_per_assessment(days),
            "roi_analysis": self.calculate_roi(),
            "anomalies": [
                {
                    "type": a.anomaly_type,
                    "severity": a.severity,
                    "description": a.description,
                    "deviation": f"{a.deviation_percentage:.1f}%"
                }
                for a in self.identify_cost_anomalies(days)
            ],
            "forecast": self.forecast_costs(30),
            "feature_profitability": self.get_feature_profitability(days)
        }


# Global analytics instance
cost_analytics = CostAnalytics()
