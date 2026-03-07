"""
Admin Cost Management API
Provides endpoints for cost monitoring, budgets, and optimization insights
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

from api_admin import verify_admin_token
from cost_tracker import cost_tracker, FeatureType, ServiceType
from cost_optimizer import cost_optimizer, Optimization
from budget_alerts import budget_monitor, BudgetStatus, AlertLevel
from cost_analytics import cost_analytics, CostAnomaly


router = APIRouter(prefix="/api/admin/costs", tags=["admin", "costs"])


# ── Pydantic Models ──────────────────────────────────────────────────────────

class CostSummaryResponse(BaseModel):
    """Summary of current costs"""
    today: float
    this_week: float
    this_month: float
    projected_monthly: float
    budget: float
    budget_status: str
    top_cost_drivers: List[Dict[str, any]]


class CostBreakdownResponse(BaseModel):
    """Detailed cost breakdown"""
    period: str
    total_cost: float
    by_service: Dict[str, float]
    by_feature: Dict[str, float]


class CostTrendData(BaseModel):
    """Cost trend data point"""
    date: str
    total: float
    anthropic: float
    database: float
    hosting: float


class OptimizationResponse(BaseModel):
    """Optimization recommendation"""
    category: str
    priority: str
    title: str
    description: str
    current_cost: float
    potential_savings: float
    implementation_effort: str
    impact: str
    action_items: List[str]


class BudgetStatusResponse(BaseModel):
    """Current budget status"""
    current_spend: float
    budget: float
    percentage_used: float
    projected_monthly: float
    alert_level: str
    days_into_month: int
    days_remaining: int
    daily_burn_rate: float
    recommended_daily_budget: float


class BudgetConfigRequest(BaseModel):
    """Budget configuration request"""
    monthly_budget: float = Field(..., gt=0, description="Monthly budget in USD")
    alert_thresholds: Optional[List[float]] = Field(default=[50, 80, 100], description="Alert threshold percentages")


class AnthropicStatsResponse(BaseModel):
    """Anthropic API statistics"""
    total_calls: int
    total_cost: float
    total_input_tokens: int
    total_output_tokens: int
    avg_tokens_per_call: int
    avg_cost_per_call: float
    cache_hit_rate: float
    cost_by_feature: Dict[str, float]
    calls_by_model: Dict[str, Dict]


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=CostSummaryResponse)
async def get_cost_summary(session: dict = Depends(verify_admin_token)):
    """
    Get cost summary overview

    Returns:
    - Today's costs
    - This week's costs
    - This month's costs
    - Projected monthly costs
    - Budget status
    - Top cost drivers
    """
    # Get daily and monthly costs
    today_costs = cost_tracker.get_daily_costs()
    monthly_costs = cost_tracker.get_monthly_costs()

    # Get week costs (last 7 days)
    week_trends = cost_tracker.get_cost_trends(7)
    week_total = sum(day["total"] for day in week_trends)

    # Get budget status
    budget_status = budget_monitor.check_budget_status()

    # Get cost breakdown by feature
    feature_breakdown = cost_tracker.get_cost_breakdown_by_feature(30)
    total_feature_cost = sum(feature_breakdown.values())

    # Calculate top cost drivers
    top_drivers = []
    for feature, cost in sorted(feature_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (cost / total_feature_cost * 100) if total_feature_cost > 0 else 0
        top_drivers.append({
            "feature": feature.replace("_", " ").title(),
            "cost": round(cost, 2),
            "percentage": round(percentage, 1)
        })

    return CostSummaryResponse(
        today=round(today_costs.get("total", 0), 2),
        this_week=round(week_total, 2),
        this_month=round(monthly_costs.get("total", 0), 2),
        projected_monthly=round(budget_status.projected_monthly, 2),
        budget=budget_status.budget,
        budget_status=budget_status.alert_level.value,
        top_cost_drivers=top_drivers
    )


@router.get("/breakdown", response_model=CostBreakdownResponse)
async def get_cost_breakdown(
    period: str = "month",  # day, week, month
    session: dict = Depends(verify_admin_token)
):
    """
    Get detailed cost breakdown by service and feature

    Args:
        period: Time period (day, week, month)

    Returns:
        Detailed breakdown of costs
    """
    if period == "day":
        costs = cost_tracker.get_daily_costs()
        days = 1
    elif period == "week":
        trends = cost_tracker.get_cost_trends(7)
        costs = {
            "anthropic": sum(d["anthropic"] for d in trends),
            "database": sum(d["database"] for d in trends),
            "hosting": sum(d["hosting"] for d in trends),
            "total": sum(d["total"] for d in trends)
        }
        days = 7
    else:  # month
        costs = cost_tracker.get_monthly_costs()
        days = 30

    # Get feature breakdown
    feature_costs = cost_tracker.get_cost_breakdown_by_feature(days)

    # Build service breakdown
    by_service = {
        "Anthropic API": round(costs.get("anthropic", 0), 2),
        "Database": round(costs.get("database", 0), 2),
        "Hosting": round(costs.get("hosting", 0), 2),
    }

    # Build feature breakdown
    by_feature = {
        feature.replace("_", " ").title(): round(cost, 2)
        for feature, cost in feature_costs.items()
    }

    return CostBreakdownResponse(
        period=period,
        total_cost=round(costs.get("total", 0), 2),
        by_service=by_service,
        by_feature=by_feature
    )


@router.get("/trends", response_model=List[CostTrendData])
async def get_cost_trends(
    days: int = 30,
    session: dict = Depends(verify_admin_token)
):
    """
    Get historical cost trends

    Args:
        days: Number of days of history (default: 30)

    Returns:
        Daily cost data for charts
    """
    trends = cost_tracker.get_cost_trends(days)

    return [
        CostTrendData(
            date=trend["date"],
            total=round(trend["total"], 2),
            anthropic=round(trend["anthropic"], 2),
            database=round(trend["database"], 2),
            hosting=round(trend["hosting"], 2)
        )
        for trend in trends
    ]


@router.get("/optimizations", response_model=List[OptimizationResponse])
async def get_optimization_suggestions(
    days: int = 30,
    session: dict = Depends(verify_admin_token)
):
    """
    Get AI-powered optimization recommendations

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        List of actionable optimization recommendations
    """
    optimizations = cost_optimizer.suggest_optimizations(days)

    return [
        OptimizationResponse(
            category=opt.category,
            priority=opt.priority,
            title=opt.title,
            description=opt.description,
            current_cost=round(opt.current_cost, 2),
            potential_savings=round(opt.potential_savings, 2),
            implementation_effort=opt.implementation_effort,
            impact=opt.impact,
            action_items=opt.action_items
        )
        for opt in optimizations
    ]


@router.get("/budget/status", response_model=BudgetStatusResponse)
async def get_budget_status(session: dict = Depends(verify_admin_token)):
    """
    Get current budget status

    Returns:
        Detailed budget metrics including burn rate and projections
    """
    status = budget_monitor.check_budget_status()

    return BudgetStatusResponse(
        current_spend=status.current_spend,
        budget=status.budget,
        percentage_used=status.percentage_used,
        projected_monthly=status.projected_monthly,
        alert_level=status.alert_level.value,
        days_into_month=status.days_into_month,
        days_remaining=status.days_remaining,
        daily_burn_rate=status.daily_burn_rate,
        recommended_daily_budget=status.recommended_daily_budget
    )


@router.post("/budget/configure")
async def configure_budget(
    config: BudgetConfigRequest,
    session: dict = Depends(verify_admin_token)
):
    """
    Configure monthly budget and alert thresholds

    Args:
        config: Budget configuration

    Returns:
        Success message
    """
    # Set budget
    budget_monitor.set_budget(config.monthly_budget)

    # Set alert thresholds
    if config.alert_thresholds:
        budget_monitor.set_alert_thresholds(config.alert_thresholds)

    # Check if alert needed
    alert = budget_monitor.send_alert_if_needed()

    return {
        "status": "success",
        "message": f"Budget set to ${config.monthly_budget:.2f}/month",
        "alert_thresholds": config.alert_thresholds,
        "alert_triggered": alert is not None
    }


@router.get("/budget/forecast")
async def get_budget_forecast(
    days_ahead: int = 30,
    session: dict = Depends(verify_admin_token)
):
    """
    Get budget forecast for upcoming period

    Args:
        days_ahead: Number of days to forecast (default: 30)

    Returns:
        Forecast data with projections
    """
    forecast = budget_monitor.get_budget_forecast(days_ahead)

    return forecast


@router.get("/anthropic/stats", response_model=AnthropicStatsResponse)
async def get_anthropic_stats(
    days: int = 30,
    session: dict = Depends(verify_admin_token)
):
    """
    Get detailed Anthropic API statistics

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Detailed API usage metrics
    """
    stats = cost_tracker.get_anthropic_stats(days)

    return AnthropicStatsResponse(**stats)


@router.get("/analytics/per-assessment")
async def get_cost_per_assessment(
    days: int = 30,
    session: dict = Depends(verify_admin_token)
):
    """
    Get cost per assessment metrics

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Average cost per completed assessment
    """
    metrics = cost_analytics.calculate_cost_per_assessment(days)

    return metrics


@router.get("/analytics/per-user")
async def get_cost_per_user(
    days: int = 30,
    session: dict = Depends(verify_admin_token)
):
    """
    Get cost per user metrics

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Average cost per user
    """
    metrics = cost_analytics.calculate_cost_per_user(days)

    return metrics


@router.get("/analytics/anomalies")
async def get_cost_anomalies(
    days: int = 30,
    sensitivity: float = 2.0,
    session: dict = Depends(verify_admin_token)
):
    """
    Detect cost anomalies and unusual patterns

    Args:
        days: Number of days to analyze (default: 30)
        sensitivity: Detection sensitivity in standard deviations (default: 2.0)

    Returns:
        List of detected anomalies
    """
    anomalies = cost_analytics.identify_cost_anomalies(days, sensitivity)

    return [
        {
            "timestamp": a.timestamp.isoformat(),
            "type": a.anomaly_type,
            "severity": a.severity,
            "description": a.description,
            "current_value": round(a.current_value, 2),
            "expected_value": round(a.expected_value, 2),
            "deviation_percentage": round(a.deviation_percentage, 1),
            "suggested_actions": a.suggested_actions
        }
        for a in anomalies
    ]


@router.get("/analytics/forecast")
async def get_cost_forecast(
    days_ahead: int = 30,
    method: str = "linear",
    session: dict = Depends(verify_admin_token)
):
    """
    Forecast future costs based on trends

    Args:
        days_ahead: Number of days to forecast (default: 30)
        method: Forecasting method (linear, moving_average)

    Returns:
        Cost forecast data
    """
    if method not in ["linear", "moving_average"]:
        raise HTTPException(status_code=400, detail="Invalid method. Use 'linear' or 'moving_average'")

    forecast = cost_analytics.forecast_costs(days_ahead, method)

    return forecast


@router.get("/analytics/roi")
async def get_roi_analysis(
    revenue_per_assessment: Optional[float] = None,
    session: dict = Depends(verify_admin_token)
):
    """
    Get ROI analysis

    Args:
        revenue_per_assessment: Optional revenue per assessment for profit calculation

    Returns:
        ROI metrics
    """
    roi = cost_analytics.calculate_roi(revenue_per_assessment)

    return roi


@router.get("/analytics/comprehensive")
async def get_comprehensive_analytics(
    days: int = 30,
    session: dict = Depends(verify_admin_token)
):
    """
    Get comprehensive cost analytics report

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Complete analytics report
    """
    report = cost_analytics.generate_comprehensive_report(days)

    return report


@router.post("/track/anthropic")
async def track_anthropic_call_manual(
    model: str,
    input_tokens: int,
    output_tokens: int,
    purpose: str,
    user_id: Optional[str] = None,
    assessment_id: Optional[str] = None,
    cache_hit: bool = False,
    session: dict = Depends(verify_admin_token)
):
    """
    Manually track an Anthropic API call (for testing/backfilling)

    Args:
        model: Model identifier
        input_tokens: Input token count
        output_tokens: Output token count
        purpose: Feature purpose
        user_id: Optional user ID
        assessment_id: Optional assessment ID
        cache_hit: Whether cache was hit

    Returns:
        Calculated cost
    """
    cost = cost_tracker.track_anthropic_call(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        purpose=purpose,
        user_id=user_id,
        assessment_id=assessment_id,
        cache_hit=cache_hit
    )

    return {
        "status": "tracked",
        "cost": round(cost, 4),
        "model": model,
        "total_tokens": input_tokens + output_tokens
    }


@router.get("/export")
async def export_cost_data(
    session: dict = Depends(verify_admin_token)
):
    """
    Export all cost tracking data

    Returns:
        Complete cost data export
    """
    data = cost_tracker.export_data()

    return {
        "exported_at": datetime.utcnow().isoformat(),
        "total_calls": len(data["calls"]),
        "data": data
    }


@router.get("/health")
async def cost_system_health(
    session: dict = Depends(verify_admin_token)
):
    """
    Check cost tracking system health

    Returns:
        System health metrics
    """
    stats = cost_tracker.get_anthropic_stats(7)
    budget_status = budget_monitor.check_budget_status()

    return {
        "status": "healthy",
        "tracking_active": True,
        "calls_last_7_days": stats["total_calls"],
        "budget_configured": budget_status.budget > 0,
        "budget_status": budget_status.alert_level.value,
        "timestamp": datetime.utcnow().isoformat()
    }
