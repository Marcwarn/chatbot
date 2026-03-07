"""
Cost Optimizer - Analyze usage patterns and suggest optimizations
Identifies inefficiencies and provides actionable cost-saving recommendations
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from cost_tracker import cost_tracker, FeatureType, ServiceType


@dataclass
class Optimization:
    """Optimization recommendation"""
    category: str  # "caching", "prompts", "architecture", "pricing"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    current_cost: float
    potential_savings: float  # Monthly savings in USD
    implementation_effort: str  # "easy", "moderate", "complex"
    impact: str  # Description of business impact
    action_items: List[str]


class CostOptimizer:
    """
    Analyze API usage and suggest optimizations

    Analyzes:
    - Cache hit rates
    - Prompt efficiency
    - Token usage patterns
    - Feature-wise cost distribution
    - Unusual usage patterns
    """

    def __init__(self, tracker=None):
        """
        Initialize cost optimizer

        Args:
            tracker: CostTracker instance (uses global if None)
        """
        self.tracker = tracker or cost_tracker

    def analyze_ai_usage(self, days: int = 30) -> Dict:
        """
        Analyze AI usage patterns and identify inefficiencies

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with analysis results
        """
        stats = self.tracker.get_anthropic_stats(days)

        if stats["total_calls"] == 0:
            return {
                "status": "no_data",
                "message": "No AI usage data available for analysis"
            }

        # Calculate metrics
        avg_tokens = stats["avg_tokens_per_call"]
        cache_hit_rate = stats["cache_hit_rate"]
        cost_by_feature = stats["cost_by_feature"]

        # Identify issues
        issues = []
        opportunities = []

        # Check cache hit rate
        if cache_hit_rate < 30:
            issues.append({
                "type": "low_cache_hit_rate",
                "severity": "high",
                "value": cache_hit_rate,
                "message": f"Cache hit rate is only {cache_hit_rate}%. Target: >50%"
            })

        # Check average tokens per call
        if avg_tokens > 3000:
            issues.append({
                "type": "high_token_usage",
                "severity": "medium",
                "value": avg_tokens,
                "message": f"Average {avg_tokens} tokens per call. Consider optimizing prompts."
            })

        # Check if report generation dominates costs
        report_cost = cost_by_feature.get("report_generation", 0)
        total_cost = sum(cost_by_feature.values())
        if report_cost > total_cost * 0.8:
            opportunities.append({
                "type": "report_caching",
                "potential": "high",
                "message": f"Report generation is {(report_cost/total_cost)*100:.1f}% of AI costs. Increase caching."
            })

        return {
            "status": "analyzed",
            "period_days": days,
            "total_cost": stats["total_cost"],
            "total_calls": stats["total_calls"],
            "metrics": {
                "avg_tokens_per_call": avg_tokens,
                "cache_hit_rate": cache_hit_rate,
                "avg_cost_per_call": stats["avg_cost_per_call"]
            },
            "issues": issues,
            "opportunities": opportunities
        }

    def suggest_optimizations(self, days: int = 30) -> List[Optimization]:
        """
        Generate actionable optimization recommendations

        Args:
            days: Number of days to analyze

        Returns:
            List of optimization recommendations
        """
        optimizations = []

        # Get usage analysis
        analysis = self.analyze_ai_usage(days)
        if analysis["status"] == "no_data":
            return optimizations

        stats = self.tracker.get_anthropic_stats(days)
        monthly_cost = stats["total_cost"] * (30 / days)  # Normalize to monthly

        # 1. Cache optimization
        cache_hit_rate = stats["cache_hit_rate"]
        if cache_hit_rate < 50:
            # Calculate potential savings
            current_monthly = monthly_cost
            # If we increase cache hit rate from X% to 60%, we save (60-X)% of costs
            target_cache_rate = 60
            potential_savings = current_monthly * ((target_cache_rate - cache_hit_rate) / 100) * 0.9

            optimizations.append(Optimization(
                category="caching",
                priority="high",
                title="Increase Cache Hit Rate",
                description=f"Current cache hit rate is {cache_hit_rate}%. Increasing to {target_cache_rate}% could save ${potential_savings:.2f}/month.",
                current_cost=monthly_cost,
                potential_savings=potential_savings,
                implementation_effort="easy",
                impact="Reduces API costs by caching frequently requested reports for 24h instead of 1h",
                action_items=[
                    "Increase cache TTL from 1h to 24h for completed reports",
                    "Implement cache warming for popular assessment types",
                    "Add cache hit/miss metrics to admin dashboard",
                    "Consider Redis for distributed caching in production"
                ]
            ))

        # 2. Prompt optimization
        avg_tokens = stats["avg_tokens_per_call"]
        if avg_tokens > 2500:
            # Estimate tokens are 60% input, 40% output
            input_tokens = avg_tokens * 0.6
            if input_tokens > 1500:
                # Reduce prompt from 1500 to 1000 tokens = 33% reduction
                token_reduction = 0.33
                potential_savings = monthly_cost * token_reduction * 0.6  # Only affects input tokens

                optimizations.append(Optimization(
                    category="prompts",
                    priority="medium",
                    title="Optimize Report Generation Prompts",
                    description=f"Average {int(avg_tokens)} tokens per call. Reducing prompt size by 33% could save ${potential_savings:.2f}/month.",
                    current_cost=monthly_cost,
                    potential_savings=potential_savings,
                    implementation_effort="moderate",
                    impact="Maintains report quality while reducing token usage",
                    action_items=[
                        "Review and compress system prompts",
                        "Remove redundant instructions from prompts",
                        "Use more efficient prompt engineering techniques",
                        "A/B test shorter prompts to ensure quality maintained",
                        "Consider using prompt templates with variable substitution"
                    ]
                ))

        # 3. Streaming responses
        chat_cost = stats["cost_by_feature"].get("chat", 0)
        if chat_cost > monthly_cost * 0.15:  # Chat is >15% of costs
            optimizations.append(Optimization(
                category="architecture",
                priority="medium",
                title="Enable Streaming for Chat Responses",
                description="Streaming responses improve UX without increasing costs, making users perceive faster service.",
                current_cost=chat_cost * (30 / days),
                potential_savings=0.0,  # No cost savings, but UX improvement
                implementation_effort="easy",
                impact="Significantly improves perceived response time and user satisfaction",
                action_items=[
                    "Implement streaming API for chat endpoints",
                    "Update frontend to handle server-sent events",
                    "Add loading indicators during streaming",
                    "Test streaming with various network conditions"
                ]
            ))

        # 4. Model selection
        if stats["calls_by_model"]:
            # Check if we're using expensive models for simple tasks
            for model, model_stats in stats["calls_by_model"].items():
                if "opus" in model.lower():
                    # Using Opus - check if we could use Sonnet
                    opus_cost = model_stats["cost"] * (30 / days)
                    # Opus is 5x more expensive than Sonnet
                    potential_savings = opus_cost * 0.8  # Could save 80% by switching

                    optimizations.append(Optimization(
                        category="pricing",
                        priority="high",
                        title=f"Optimize Model Selection - Review {model} Usage",
                        description=f"Using premium model for ${opus_cost:.2f}/month. Could save ${potential_savings:.2f}/month by using Sonnet for appropriate tasks.",
                        current_cost=opus_cost,
                        potential_savings=potential_savings,
                        implementation_effort="easy",
                        impact="Significant cost reduction while maintaining quality for most use cases",
                        action_items=[
                            "Audit which features actually need Opus-level quality",
                            "Switch chat to Claude Sonnet (5x cheaper)",
                            "Keep Opus only for complex report generation if needed",
                            "Implement A/B test to compare quality vs cost",
                            "Monitor user satisfaction metrics after switch"
                        ]
                    ))

        # 5. Batch processing
        total_calls = stats["total_calls"]
        if total_calls > 1000:  # High volume
            # Estimate 10% savings from batching
            potential_savings = monthly_cost * 0.10

            optimizations.append(Optimization(
                category="architecture",
                priority="low",
                title="Implement Batch Processing for Reports",
                description=f"Processing {total_calls} calls. Batching similar requests could save ${potential_savings:.2f}/month.",
                current_cost=monthly_cost,
                potential_savings=potential_savings,
                implementation_effort="complex",
                impact="Reduces costs through request batching and better resource utilization",
                action_items=[
                    "Identify common report patterns that can be batched",
                    "Implement queue system for non-urgent report generation",
                    "Add batch processing during off-peak hours",
                    "Cache common report templates",
                    "Consider async report generation with notifications"
                ]
            ))

        # 6. Token usage monitoring
        optimizations.append(Optimization(
            category="monitoring",
            priority="high",
            title="Set Up Cost Alerts and Budgets",
            description="Proactive monitoring prevents cost overruns and enables quick response to anomalies.",
            current_cost=0.0,
            potential_savings=monthly_cost * 0.2,  # Prevent 20% waste through monitoring
            implementation_effort="easy",
            impact="Prevents unexpected cost spikes and enables data-driven optimization",
            action_items=[
                "Set monthly budget alert at $500",
                "Configure alerts at 50%, 80%, 100% of budget",
                "Set up anomaly detection for unusual usage spikes",
                "Create daily cost report email for admins",
                "Monitor cost per assessment metric weekly"
            ]
        ))

        # Sort by potential savings
        optimizations.sort(key=lambda x: x.potential_savings, reverse=True)

        return optimizations

    def detect_anomalies(self, days: int = 7) -> List[Dict]:
        """
        Detect unusual cost patterns and potential abuse

        Args:
            days: Number of days to analyze

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Get recent costs
        trends = self.tracker.get_cost_trends(days)
        if len(trends) < 3:
            return anomalies

        # Calculate daily averages
        daily_costs = [t["total"] for t in trends]
        avg_daily = sum(daily_costs) / len(daily_costs)
        max_daily = max(daily_costs)

        # Check for sudden spikes (>3x average)
        spike_threshold = avg_daily * 3
        for trend in trends:
            if trend["total"] > spike_threshold:
                anomalies.append({
                    "type": "cost_spike",
                    "severity": "high",
                    "date": trend["date"],
                    "cost": trend["total"],
                    "average": avg_daily,
                    "message": f"Cost spike detected: ${trend['total']:.2f} vs avg ${avg_daily:.2f}"
                })

        # Check for sustained high usage
        if max_daily > avg_daily * 2 and all(c > avg_daily * 1.5 for c in daily_costs[-3:]):
            anomalies.append({
                "type": "sustained_high_usage",
                "severity": "medium",
                "message": f"Sustained high usage detected over last 3 days",
                "avg_cost": avg_daily,
                "recent_avg": sum(daily_costs[-3:]) / 3
            })

        # Check for zero-cost days (potential tracking issue)
        zero_days = sum(1 for c in daily_costs if c == 0)
        if zero_days > 0:
            anomalies.append({
                "type": "tracking_gap",
                "severity": "low",
                "message": f"{zero_days} days with zero costs - possible tracking issue",
                "zero_days": zero_days
            })

        return anomalies

    def get_optimization_summary(self, days: int = 30) -> Dict:
        """
        Get comprehensive optimization summary

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with optimization summary
        """
        optimizations = self.suggest_optimizations(days)
        anomalies = self.detect_anomalies(days)
        analysis = self.analyze_ai_usage(days)

        total_potential_savings = sum(opt.potential_savings for opt in optimizations)

        return {
            "period_days": days,
            "current_monthly_cost": analysis.get("total_cost", 0) * (30 / days),
            "potential_monthly_savings": total_potential_savings,
            "optimization_count": len(optimizations),
            "anomaly_count": len(anomalies),
            "high_priority_optimizations": [
                {
                    "title": opt.title,
                    "savings": opt.potential_savings,
                    "effort": opt.implementation_effort
                }
                for opt in optimizations if opt.priority == "high"
            ],
            "recent_anomalies": anomalies,
            "top_recommendation": optimizations[0].title if optimizations else None
        }


# Global optimizer instance
cost_optimizer = CostOptimizer()
