#!/usr/bin/env python3
"""
Cost Tracking System Verification Script
Demonstrates all features of the cost tracking system
"""

from cost_tracker import cost_tracker
from cost_optimizer import cost_optimizer
from budget_alerts import budget_monitor
from cost_analytics import cost_analytics


def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    print("\n🎯 Cost Tracking System Verification\n")

    # 1. Track some API calls
    print_section("1. Tracking API Calls")

    print("Simulating 10 report generations...")
    for i in range(10):
        cost = cost_tracker.track_anthropic_call(
            model="claude-sonnet-4-5-20250929",
            input_tokens=2000 + (i * 100),
            output_tokens=1000,
            purpose="report_generation",
            user_id=f"user_{i % 3}",
            assessment_id=f"assessment_{i}",
            cache_hit=(i % 4 == 0)  # 25% cache hit
        )
        print(f"  Call {i+1}: ${cost:.4f}")

    print("\nSimulating 5 chat conversations...")
    for i in range(5):
        cost = cost_tracker.track_anthropic_call(
            model="claude-sonnet-4-5-20250929",
            input_tokens=500,
            output_tokens=300,
            purpose="chat",
            user_id=f"user_{i % 2}",
            cache_hit=False
        )
        print(f"  Chat {i+1}: ${cost:.4f}")

    # 2. Cost Summary
    print_section("2. Cost Summary")

    daily = cost_tracker.get_daily_costs()
    print(f"Today's Costs:")
    print(f"  Anthropic API: ${daily['anthropic']:.2f}")
    print(f"  Database:      ${daily['database']:.2f}")
    print(f"  Hosting:       ${daily['hosting']:.2f}")
    print(f"  TOTAL:         ${daily['total']:.2f}")

    # 3. Anthropic Statistics
    print_section("3. Anthropic API Statistics")

    stats = cost_tracker.get_anthropic_stats(30)
    print(f"Total Calls:           {stats['total_calls']}")
    print(f"Total Cost:            ${stats['total_cost']:.2f}")
    print(f"Avg Tokens per Call:   {stats['avg_tokens_per_call']}")
    print(f"Avg Cost per Call:     ${stats['avg_cost_per_call']:.4f}")
    print(f"Cache Hit Rate:        {stats['cache_hit_rate']:.1f}%")

    print(f"\nCost by Feature:")
    for feature, cost in stats['cost_by_feature'].items():
        percentage = (cost / stats['total_cost'] * 100) if stats['total_cost'] > 0 else 0
        print(f"  {feature:20} ${cost:6.2f} ({percentage:5.1f}%)")

    # 4. Budget Configuration
    print_section("4. Budget Monitoring")

    print("Setting monthly budget to $500...")
    budget_monitor.set_budget(500.00)
    budget_monitor.set_alert_thresholds([50, 80, 100])

    status = budget_monitor.check_budget_status()
    print(f"\nBudget Status:")
    print(f"  Current Spend:         ${status.current_spend:.2f}")
    print(f"  Monthly Budget:        ${status.budget:.2f}")
    print(f"  Percentage Used:       {status.percentage_used:.1f}%")
    print(f"  Alert Level:           {status.alert_level.value.upper()}")
    print(f"  Daily Burn Rate:       ${status.daily_burn_rate:.2f}")
    print(f"  Projected Monthly:     ${status.projected_monthly:.2f}")
    print(f"  Days Remaining:        {status.days_remaining}")
    print(f"  Recommended Daily:     ${status.recommended_daily_budget:.2f}")

    # 5. Cost Analytics
    print_section("5. Cost Analytics")

    # Cost per user
    user_metrics = cost_analytics.calculate_cost_per_user(30)
    print(f"Cost per User:")
    print(f"  Total Users:           {user_metrics['total_users']}")
    print(f"  Average Cost/User:     ${user_metrics['avg_cost_per_user']:.4f}")
    if user_metrics['max_cost_user']:
        print(f"  Max Cost User:         {user_metrics['max_cost_user']['user_id']}")
        print(f"  Max Cost:              ${user_metrics['max_cost_user']['cost']:.2f}")

    # Cost per assessment
    assessment_metrics = cost_analytics.calculate_cost_per_assessment(30)
    print(f"\nCost per Assessment:")
    print(f"  Total Assessments:     {assessment_metrics['total_assessments']}")
    print(f"  Average Cost:          ${assessment_metrics['avg_cost_per_assessment']:.4f}")

    # ROI analysis
    roi = cost_analytics.calculate_roi(revenue_per_assessment=2.00)
    if 'profit_per_assessment' in roi:
        print(f"\nROI Analysis (@ $2.00 revenue/assessment):")
        print(f"  Profit/Assessment:     ${roi['profit_per_assessment']:.4f}")
        print(f"  Profit Margin:         {roi['profit_margin']:.1f}%")
        print(f"  Monthly Revenue:       ${roi['monthly_revenue']:.2f}")
        print(f"  Monthly Profit:        ${roi['monthly_profit']:.2f}")
        print(f"  ROI:                   {roi['roi_percentage']:.1f}%")

    # 6. Optimization Suggestions
    print_section("6. Optimization Recommendations")

    optimizations = cost_optimizer.suggest_optimizations(30)
    print(f"Found {len(optimizations)} optimization opportunities:\n")

    for i, opt in enumerate(optimizations[:3], 1):  # Show top 3
        print(f"{i}. {opt.title}")
        print(f"   Category:     {opt.category}")
        print(f"   Priority:     {opt.priority.upper()}")
        print(f"   Savings:      ${opt.potential_savings:.2f}/month")
        print(f"   Effort:       {opt.implementation_effort}")
        print(f"   Impact:       {opt.impact}")
        print(f"   Actions:")
        for action in opt.action_items[:2]:  # Show first 2 actions
            print(f"     • {action}")
        print()

    # 7. Cost Forecast
    print_section("7. Cost Forecast")

    forecast = cost_analytics.forecast_costs(days_ahead=30, method="linear")
    if forecast['status'] == 'success':
        print(f"30-Day Forecast:")
        print(f"  Current Daily Avg:     ${forecast['current_daily_avg']:.2f}")
        print(f"  Forecasted Daily Avg:  ${forecast['forecasted_daily_avg']:.2f}")
        print(f"  Current Month Cost:    ${forecast['current_month_cost']:.2f}")
        print(f"  Projected Month End:   ${forecast['projected_month_end']:.2f}")
        print(f"  Confidence:            {forecast['confidence'].upper()}")

        # Show first 7 days of forecast
        print(f"\n  Next 7 Days:")
        for day in forecast['forecast'][:7]:
            print(f"    {day['date']}: ${day['forecasted_cost']:.2f}")

    # 8. Summary
    print_section("8. Summary")

    total_savings = sum(opt.potential_savings for opt in optimizations)
    print(f"✅ Cost tracking system is operational!")
    print(f"\n📊 Current Metrics:")
    print(f"   • Total calls tracked:    {stats['total_calls']}")
    print(f"   • Total cost:             ${stats['total_cost']:.2f}")
    print(f"   • Cache hit rate:         {stats['cache_hit_rate']:.1f}%")
    print(f"   • Budget status:          {status.alert_level.value.upper()}")
    print(f"\n💡 Optimization Potential:")
    print(f"   • {len(optimizations)} opportunities identified")
    print(f"   • Potential savings:      ${total_savings:.2f}/month")
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review optimization recommendations")
    print(f"   2. Implement high-priority actions")
    print(f"   3. Monitor budget alerts")
    print(f"   4. Track cost trends daily")

    print(f"\n{'='*60}")
    print(f"  Verification Complete! ✅")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
