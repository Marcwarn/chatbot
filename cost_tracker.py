"""
Cost Tracker - Real-time API usage and cost monitoring
Tracks Anthropic API calls, database operations, and other service costs
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class ServiceType(Enum):
    """Types of services tracked"""
    ANTHROPIC = "anthropic"
    DATABASE = "database"
    HOSTING = "hosting"
    SENTRY = "sentry"
    REDIS = "redis"
    S3 = "s3"


class FeatureType(Enum):
    """Feature categories for cost attribution"""
    REPORT_GENERATION = "report_generation"
    CHAT = "chat"
    ADMIN_ANALYTICS = "admin_analytics"
    DATA_EXPORT = "data_export"
    SECURITY_MONITORING = "security_monitoring"


@dataclass
class APICall:
    """Record of a single API call"""
    timestamp: datetime
    service: ServiceType
    feature: FeatureType
    model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost: float = 0.0
    user_id: Optional[str] = None
    assessment_id: Optional[str] = None
    cache_hit: bool = False
    metadata: Optional[Dict] = None


class CostTracker:
    """
    Track API usage and costs in real-time

    Features:
    - Track all API calls with detailed metrics
    - Calculate costs based on current pricing
    - Aggregate by service, feature, time period
    - Support for cache hit tracking
    - Memory-efficient rolling window storage
    """

    # Anthropic API Pricing (as of 2026-03)
    # Source: https://www.anthropic.com/pricing
    ANTHROPIC_PRICING = {
        "claude-sonnet-4-5-20250929": {
            "input": 0.003,   # $ per 1K tokens
            "output": 0.015,  # $ per 1K tokens
        },
        "claude-opus-4": {
            "input": 0.015,
            "output": 0.075,
        },
        "claude-haiku-3-5": {
            "input": 0.001,
            "output": 0.005,
        }
    }

    # Database pricing estimates (Vercel Postgres)
    DATABASE_PRICING = {
        "storage_per_gb": 0.25,      # $ per GB per month
        "compute_per_hour": 0.01,    # $ per compute hour
        "query_cost": 0.000001,      # $ per query (estimate)
    }

    # Hosting pricing (Vercel Pro tier)
    HOSTING_PRICING = {
        "bandwidth_per_gb": 0.15,    # $ per GB
        "function_exec": 0.00002,    # $ per execution
        "function_gb_hour": 0.0000185, # $ per GB-hour
    }

    def __init__(self, retention_days: int = 90):
        """
        Initialize cost tracker

        Args:
            retention_days: How long to keep detailed call records (default 90 days)
        """
        self.retention_days = retention_days
        self._calls: List[APICall] = []
        self._daily_aggregates: Dict[str, Dict] = {}  # date -> aggregated stats

    def track_anthropic_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        purpose: str,
        user_id: Optional[str] = None,
        assessment_id: Optional[str] = None,
        cache_hit: bool = False,
        metadata: Optional[Dict] = None
    ) -> float:
        """
        Track an Anthropic API call and calculate cost

        Args:
            model: Model identifier (e.g., "claude-sonnet-4-5-20250929")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            purpose: Feature using the API (report_generation, chat, etc.)
            user_id: Optional user ID
            assessment_id: Optional assessment ID
            cache_hit: Whether this used cached response
            metadata: Additional metadata

        Returns:
            Cost in USD
        """
        # Calculate cost
        pricing = self.ANTHROPIC_PRICING.get(model, self.ANTHROPIC_PRICING["claude-sonnet-4-5-20250929"])
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        # Apply cache discount (cache hits typically reduce input tokens by ~90%)
        if cache_hit:
            total_cost *= 0.1  # Approximate cache savings

        # Map purpose string to FeatureType
        feature_map = {
            "report_generation": FeatureType.REPORT_GENERATION,
            "chat": FeatureType.CHAT,
            "admin_analytics": FeatureType.ADMIN_ANALYTICS,
            "data_export": FeatureType.DATA_EXPORT,
            "security_monitoring": FeatureType.SECURITY_MONITORING,
        }
        feature = feature_map.get(purpose, FeatureType.REPORT_GENERATION)

        # Create call record
        call = APICall(
            timestamp=datetime.utcnow(),
            service=ServiceType.ANTHROPIC,
            feature=feature,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=total_cost,
            user_id=user_id,
            assessment_id=assessment_id,
            cache_hit=cache_hit,
            metadata=metadata or {}
        )

        self._calls.append(call)
        self._cleanup_old_calls()

        return total_cost

    def track_database_operation(
        self,
        operation_type: str,  # "query", "write", "storage"
        feature: str,
        size_bytes: Optional[int] = None,
        query_count: int = 1,
        execution_time_ms: Optional[float] = None
    ) -> float:
        """
        Track database operation cost

        Args:
            operation_type: Type of operation
            feature: Feature using the database
            size_bytes: Data size in bytes
            query_count: Number of queries
            execution_time_ms: Query execution time

        Returns:
            Estimated cost in USD
        """
        cost = 0.0

        if operation_type == "query":
            cost = query_count * self.DATABASE_PRICING["query_cost"]
        elif operation_type == "storage" and size_bytes:
            gb = size_bytes / (1024 ** 3)
            cost = gb * self.DATABASE_PRICING["storage_per_gb"] / 30  # Daily cost

        feature_map = {
            "report_generation": FeatureType.REPORT_GENERATION,
            "chat": FeatureType.CHAT,
            "admin_analytics": FeatureType.ADMIN_ANALYTICS,
            "data_export": FeatureType.DATA_EXPORT,
            "security_monitoring": FeatureType.SECURITY_MONITORING,
        }

        call = APICall(
            timestamp=datetime.utcnow(),
            service=ServiceType.DATABASE,
            feature=feature_map.get(feature, FeatureType.REPORT_GENERATION),
            cost=cost,
            metadata={
                "operation_type": operation_type,
                "size_bytes": size_bytes,
                "query_count": query_count,
                "execution_time_ms": execution_time_ms
            }
        )

        self._calls.append(call)
        return cost

    def track_hosting_usage(
        self,
        bandwidth_bytes: Optional[int] = None,
        function_executions: int = 0,
        function_gb_seconds: Optional[float] = None,
        feature: str = "report_generation"
    ) -> float:
        """
        Track hosting/serverless costs

        Args:
            bandwidth_bytes: Bandwidth used
            function_executions: Number of function invocations
            function_gb_seconds: Function memory-time usage
            feature: Feature using the resources

        Returns:
            Estimated cost in USD
        """
        cost = 0.0

        if bandwidth_bytes:
            gb = bandwidth_bytes / (1024 ** 3)
            cost += gb * self.HOSTING_PRICING["bandwidth_per_gb"]

        if function_executions:
            cost += function_executions * self.HOSTING_PRICING["function_exec"]

        if function_gb_seconds:
            gb_hours = function_gb_seconds / 3600
            cost += gb_hours * self.HOSTING_PRICING["function_gb_hour"]

        feature_map = {
            "report_generation": FeatureType.REPORT_GENERATION,
            "chat": FeatureType.CHAT,
            "admin_analytics": FeatureType.ADMIN_ANALYTICS,
            "data_export": FeatureType.DATA_EXPORT,
            "security_monitoring": FeatureType.SECURITY_MONITORING,
        }

        call = APICall(
            timestamp=datetime.utcnow(),
            service=ServiceType.HOSTING,
            feature=feature_map.get(feature, FeatureType.REPORT_GENERATION),
            cost=cost,
            metadata={
                "bandwidth_bytes": bandwidth_bytes,
                "function_executions": function_executions,
                "function_gb_seconds": function_gb_seconds
            }
        )

        self._calls.append(call)
        return cost

    def get_daily_costs(self, date: Optional[datetime] = None) -> Dict[str, float]:
        """
        Get costs for a specific day, broken down by service

        Args:
            date: Date to get costs for (default: today)

        Returns:
            Dictionary of service -> cost
        """
        if date is None:
            date = datetime.utcnow()

        start = datetime(date.year, date.month, date.day)
        end = start + timedelta(days=1)

        costs = {service.value: 0.0 for service in ServiceType}

        for call in self._calls:
            if start <= call.timestamp < end:
                costs[call.service.value] += call.cost

        costs["total"] = sum(costs.values())
        return costs

    def get_monthly_costs(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, float]:
        """
        Get costs for a specific month

        Args:
            year: Year (default: current)
            month: Month (default: current)

        Returns:
            Dictionary of service -> cost
        """
        now = datetime.utcnow()
        year = year or now.year
        month = month or now.month

        # Get date range for month
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)

        costs = {service.value: 0.0 for service in ServiceType}

        for call in self._calls:
            if start <= call.timestamp < end:
                costs[call.service.value] += call.cost

        costs["total"] = sum(costs.values())
        return costs

    def get_cost_breakdown_by_feature(self, days: int = 30) -> Dict[str, float]:
        """
        Get cost breakdown by feature for the last N days

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary of feature -> cost
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        costs = {feature.value: 0.0 for feature in FeatureType}

        for call in self._calls:
            if call.timestamp >= cutoff:
                costs[call.feature.value] += call.cost

        return costs

    def get_anthropic_stats(self, days: int = 30) -> Dict:
        """
        Get detailed Anthropic API statistics

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with detailed stats
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        anthropic_calls = [
            c for c in self._calls
            if c.service == ServiceType.ANTHROPIC and c.timestamp >= cutoff
        ]

        if not anthropic_calls:
            return {
                "total_calls": 0,
                "total_cost": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "avg_tokens_per_call": 0,
                "avg_cost_per_call": 0.0,
                "cache_hit_rate": 0.0,
                "cost_by_feature": {},
                "calls_by_model": {}
            }

        total_input = sum(c.input_tokens or 0 for c in anthropic_calls)
        total_output = sum(c.output_tokens or 0 for c in anthropic_calls)
        total_cost = sum(c.cost for c in anthropic_calls)
        cache_hits = sum(1 for c in anthropic_calls if c.cache_hit)

        # Cost by feature
        cost_by_feature = {}
        for call in anthropic_calls:
            feature = call.feature.value
            cost_by_feature[feature] = cost_by_feature.get(feature, 0.0) + call.cost

        # Calls by model
        calls_by_model = {}
        for call in anthropic_calls:
            model = call.model or "unknown"
            if model not in calls_by_model:
                calls_by_model[model] = {"count": 0, "cost": 0.0}
            calls_by_model[model]["count"] += 1
            calls_by_model[model]["cost"] += call.cost

        return {
            "total_calls": len(anthropic_calls),
            "total_cost": round(total_cost, 2),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "avg_tokens_per_call": round((total_input + total_output) / len(anthropic_calls)),
            "avg_cost_per_call": round(total_cost / len(anthropic_calls), 4),
            "cache_hit_rate": round((cache_hits / len(anthropic_calls)) * 100, 1),
            "cost_by_feature": cost_by_feature,
            "calls_by_model": calls_by_model
        }

    def get_cost_trends(self, days: int = 30) -> List[Dict]:
        """
        Get daily cost trends

        Args:
            days: Number of days to analyze

        Returns:
            List of daily cost records
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Group by date
        daily_costs = {}
        for call in self._calls:
            if call.timestamp >= cutoff:
                date_key = call.timestamp.strftime("%Y-%m-%d")
                if date_key not in daily_costs:
                    daily_costs[date_key] = {
                        "date": date_key,
                        "total": 0.0,
                        "anthropic": 0.0,
                        "database": 0.0,
                        "hosting": 0.0
                    }
                daily_costs[date_key]["total"] += call.cost
                daily_costs[date_key][call.service.value] += call.cost

        # Sort by date
        return sorted(daily_costs.values(), key=lambda x: x["date"])

    def get_average_cost_per_assessment(self, days: int = 30) -> Dict[str, float]:
        """
        Calculate average cost per completed assessment

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with cost metrics per assessment
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get unique assessments
        assessments = set()
        total_cost = 0.0

        for call in self._calls:
            if call.timestamp >= cutoff and call.assessment_id:
                assessments.add(call.assessment_id)
                if call.feature == FeatureType.REPORT_GENERATION:
                    total_cost += call.cost

        if not assessments:
            return {
                "total_assessments": 0,
                "total_cost": 0.0,
                "avg_cost_per_assessment": 0.0
            }

        return {
            "total_assessments": len(assessments),
            "total_cost": round(total_cost, 2),
            "avg_cost_per_assessment": round(total_cost / len(assessments), 4)
        }

    def _cleanup_old_calls(self):
        """Remove call records older than retention period"""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        self._calls = [c for c in self._calls if c.timestamp >= cutoff]

    def export_data(self) -> Dict:
        """
        Export all tracking data for persistence

        Returns:
            Dictionary with all call data
        """
        return {
            "calls": [
                {
                    "timestamp": call.timestamp.isoformat(),
                    "service": call.service.value,
                    "feature": call.feature.value,
                    "model": call.model,
                    "input_tokens": call.input_tokens,
                    "output_tokens": call.output_tokens,
                    "cost": call.cost,
                    "user_id": call.user_id,
                    "assessment_id": call.assessment_id,
                    "cache_hit": call.cache_hit,
                    "metadata": call.metadata
                }
                for call in self._calls
            ]
        }

    def import_data(self, data: Dict):
        """
        Import tracking data from storage

        Args:
            data: Dictionary with call data
        """
        for call_data in data.get("calls", []):
            call = APICall(
                timestamp=datetime.fromisoformat(call_data["timestamp"]),
                service=ServiceType(call_data["service"]),
                feature=FeatureType(call_data["feature"]),
                model=call_data.get("model"),
                input_tokens=call_data.get("input_tokens"),
                output_tokens=call_data.get("output_tokens"),
                cost=call_data["cost"],
                user_id=call_data.get("user_id"),
                assessment_id=call_data.get("assessment_id"),
                cache_hit=call_data.get("cache_hit", False),
                metadata=call_data.get("metadata", {})
            )
            self._calls.append(call)


# Global cost tracker instance
cost_tracker = CostTracker()
