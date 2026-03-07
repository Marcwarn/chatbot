"""
Admin Analytics Module
Advanced analytics for Big Five and DISC assessments
Provides insights, trends, and comparative analytics
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics


class AdminAnalytics:
    """Analytics engine for assessment data"""

    def __init__(self, analytics_data: Dict[str, Any]):
        """
        Initialize with analytics data from api_admin._analytics

        Args:
            analytics_data: Dictionary containing assessments, users, etc.
        """
        self.data = analytics_data

    # ── Big Five Analytics ──────────────────────────────────────────────────

    def get_big_five_stats(self) -> Dict[str, Any]:
        """Calculate Big Five assessment statistics"""
        bf_assessments = [
            a for a in self.data["assessments"]
            if a.get("assessment_type") == "big_five"
        ]

        if not bf_assessments:
            return {
                "total": 0,
                "avg_scores": {"E": 0, "A": 0, "C": 0, "N": 0, "O": 0},
                "score_distribution": {},
                "completion_rate": 0
            }

        # Calculate average scores
        avg_scores = {"E": 0, "A": 0, "C": 0, "N": 0, "O": 0}
        score_counts = defaultdict(lambda: defaultdict(int))

        for assessment in bf_assessments:
            scores = assessment.get("scores", {})
            for dim in ["E", "A", "C", "N", "O"]:
                if dim in scores:
                    avg_scores[dim] += scores[dim]
                    # Categorize into ranges for distribution
                    score_range = self._get_score_range(scores[dim])
                    score_counts[dim][score_range] += 1

        # Calculate averages
        count = len(bf_assessments)
        for dim in avg_scores:
            avg_scores[dim] = round(avg_scores[dim] / count, 1)

        return {
            "total": count,
            "avg_scores": avg_scores,
            "score_distribution": dict(score_counts),
            "completion_rate": self._calculate_completion_rate("big_five")
        }

    # ── DISC Analytics ──────────────────────────────────────────────────────

    def get_disc_stats(self) -> Dict[str, Any]:
        """Calculate DISC assessment statistics"""
        disc_assessments = [
            a for a in self.data["assessments"]
            if a.get("assessment_type") == "disc"
        ]

        if not disc_assessments:
            return {
                "total": 0,
                "avg_scores": {"D": 0, "I": 0, "S": 0, "C": 0},
                "profile_distribution": {},
                "dominant_profiles": [],
                "completion_rate": 0
            }

        # Calculate average scores
        avg_scores = {"D": 0, "I": 0, "S": 0, "C": 0}
        profiles = []

        for assessment in disc_assessments:
            scores = assessment.get("scores", {})

            # Add to averages
            for dim in ["D", "I", "S", "C"]:
                if dim in scores:
                    avg_scores[dim] += scores[dim]

            # Determine primary profile
            profile = self._determine_disc_profile(scores)
            if profile:
                profiles.append(profile)

        # Calculate averages
        count = len(disc_assessments)
        for dim in avg_scores:
            avg_scores[dim] = round(avg_scores[dim] / count, 1)

        # Profile distribution
        profile_dist = Counter(profiles)

        # Get top 5 dominant profiles
        dominant_profiles = [
            {"profile": profile, "count": count, "percentage": round(count / len(profiles) * 100, 1)}
            for profile, count in profile_dist.most_common(5)
        ]

        return {
            "total": count,
            "avg_scores": avg_scores,
            "profile_distribution": dict(profile_dist),
            "dominant_profiles": dominant_profiles,
            "completion_rate": self._calculate_completion_rate("disc")
        }

    def _determine_disc_profile(self, scores: Dict[str, float]) -> Optional[str]:
        """
        Determine DISC profile type based on scores

        Profiles:
        - D (Dominance): Direct, results-oriented
        - I (Influence): Enthusiastic, persuasive
        - S (Steadiness): Stable, patient
        - C (Conscientiousness): Analytical, precise
        - Di, DC, ID, IS, SC, SI, etc. (combinations)
        """
        if not scores or not all(dim in scores for dim in ["D", "I", "S", "C"]):
            return None

        # Get highest score(s)
        sorted_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        highest = sorted_dims[0]
        second = sorted_dims[1]

        # If one dimension is clearly dominant (10+ points higher)
        if highest[1] - second[1] >= 10:
            return highest[0]

        # If two dimensions are close, create combination profile
        return f"{highest[0]}{second[0]}"

    # ── Comparative Analytics ───────────────────────────────────────────────

    def get_assessment_comparison(self) -> Dict[str, Any]:
        """Compare Big Five vs DISC assessments"""
        all_assessments = self.data["assessments"]

        bf_count = sum(1 for a in all_assessments if a.get("assessment_type") == "big_five")
        disc_count = sum(1 for a in all_assessments if a.get("assessment_type") == "disc")
        other_count = len(all_assessments) - bf_count - disc_count

        total = len(all_assessments)

        return {
            "total_assessments": total,
            "big_five": {
                "count": bf_count,
                "percentage": round(bf_count / total * 100, 1) if total > 0 else 0
            },
            "disc": {
                "count": disc_count,
                "percentage": round(disc_count / total * 100, 1) if total > 0 else 0
            },
            "other": {
                "count": other_count,
                "percentage": round(other_count / total * 100, 1) if total > 0 else 0
            },
            "most_popular": self._get_most_popular_type()
        }

    def _get_most_popular_type(self) -> str:
        """Determine which assessment type is most popular"""
        type_counts = Counter(
            a.get("assessment_type", "unknown")
            for a in self.data["assessments"]
        )

        if not type_counts:
            return "none"

        most_common = type_counts.most_common(1)[0]
        return most_common[0]

    # ── Time Series Analytics ───────────────────────────────────────────────

    def get_time_series_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Get assessment trends over time

        Args:
            days: Number of days to analyze

        Returns:
            Daily breakdown of assessments by type
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Initialize daily counters
        daily_data = defaultdict(lambda: {"big_five": 0, "disc": 0, "other": 0})

        for assessment in self.data["assessments"]:
            completed_at = datetime.fromisoformat(assessment.get("completed_at"))

            if completed_at >= cutoff_date:
                date_key = completed_at.strftime("%Y-%m-%d")
                assessment_type = assessment.get("assessment_type", "other")

                if assessment_type == "big_five":
                    daily_data[date_key]["big_five"] += 1
                elif assessment_type == "disc":
                    daily_data[date_key]["disc"] += 1
                else:
                    daily_data[date_key]["other"] += 1

        # Convert to sorted list
        time_series = [
            {
                "date": date,
                **counts
            }
            for date, counts in sorted(daily_data.items())
        ]

        return {
            "period_days": days,
            "data_points": time_series,
            "total_in_period": sum(
                day["big_five"] + day["disc"] + day["other"]
                for day in time_series
            )
        }

    def get_assessments_last_24h(self) -> Dict[str, int]:
        """Get assessment counts for last 24 hours by type"""
        cutoff = datetime.utcnow() - timedelta(hours=24)

        counts = {"big_five": 0, "disc": 0, "other": 0, "total": 0}

        for assessment in self.data["assessments"]:
            completed_at = datetime.fromisoformat(assessment.get("completed_at"))

            if completed_at >= cutoff:
                assessment_type = assessment.get("assessment_type", "other")

                if assessment_type == "big_five":
                    counts["big_five"] += 1
                elif assessment_type == "disc":
                    counts["disc"] += 1
                else:
                    counts["other"] += 1

                counts["total"] += 1

        return counts

    def get_assessments_last_7d(self) -> Dict[str, int]:
        """Get assessment counts for last 7 days by type"""
        cutoff = datetime.utcnow() - timedelta(days=7)

        counts = {"big_five": 0, "disc": 0, "other": 0, "total": 0}

        for assessment in self.data["assessments"]:
            completed_at = datetime.fromisoformat(assessment.get("completed_at"))

            if completed_at >= cutoff:
                assessment_type = assessment.get("assessment_type", "other")

                if assessment_type == "big_five":
                    counts["big_five"] += 1
                elif assessment_type == "disc":
                    counts["disc"] += 1
                else:
                    counts["other"] += 1

                counts["total"] += 1

        return counts

    # ── User Demographics ───────────────────────────────────────────────────

    def get_user_demographics_by_type(self) -> Dict[str, Any]:
        """Analyze user behavior patterns by assessment type"""
        user_stats = defaultdict(lambda: {
            "big_five_count": 0,
            "disc_count": 0,
            "total_assessments": 0,
            "preferred_type": None
        })

        # Aggregate user assessment preferences
        for assessment in self.data["assessments"]:
            user_id = assessment.get("user_id")
            assessment_type = assessment.get("assessment_type", "other")

            user_stats[user_id]["total_assessments"] += 1

            if assessment_type == "big_five":
                user_stats[user_id]["big_five_count"] += 1
            elif assessment_type == "disc":
                user_stats[user_id]["disc_count"] += 1

        # Determine preferred type for each user
        for user_id, stats in user_stats.items():
            if stats["big_five_count"] > stats["disc_count"]:
                stats["preferred_type"] = "big_five"
            elif stats["disc_count"] > stats["big_five_count"]:
                stats["preferred_type"] = "disc"
            else:
                stats["preferred_type"] = "both"

        # Aggregate demographics
        preference_counts = Counter(
            stats["preferred_type"]
            for stats in user_stats.values()
        )

        avg_assessments_per_user = (
            statistics.mean(stats["total_assessments"] for stats in user_stats.values())
            if user_stats else 0
        )

        return {
            "total_users": len(user_stats),
            "preference_distribution": dict(preference_counts),
            "avg_assessments_per_user": round(avg_assessments_per_user, 1),
            "users_with_both_types": sum(
                1 for stats in user_stats.values()
                if stats["big_five_count"] > 0 and stats["disc_count"] > 0
            )
        }

    # ── Completion Rates ────────────────────────────────────────────────────

    def _calculate_completion_rate(self, assessment_type: str) -> float:
        """
        Calculate completion rate for an assessment type

        Note: Currently all assessments in analytics are completed
        This method is a placeholder for future implementation with in-progress tracking
        """
        # In production, you would track started vs completed assessments
        # For now, return a mock high completion rate
        return 95.0

    def get_completion_funnel(self) -> Dict[str, Any]:
        """
        Get conversion funnel data: Start → Complete

        Returns funnel metrics for both assessment types
        """
        # This is a simplified version - in production you'd track actual starts
        completed_bf = sum(
            1 for a in self.data["assessments"]
            if a.get("assessment_type") == "big_five"
        )
        completed_disc = sum(
            1 for a in self.data["assessments"]
            if a.get("assessment_type") == "disc"
        )

        # Mock started counts (in production, track these separately)
        started_bf = int(completed_bf * 1.05)  # Assume 95% completion
        started_disc = int(completed_disc * 1.05)

        return {
            "big_five": {
                "started": started_bf,
                "completed": completed_bf,
                "completion_rate": round(completed_bf / started_bf * 100, 1) if started_bf > 0 else 0
            },
            "disc": {
                "started": started_disc,
                "completed": completed_disc,
                "completion_rate": round(completed_disc / started_disc * 100, 1) if started_disc > 0 else 0
            }
        }

    # ── Helper Methods ──────────────────────────────────────────────────────

    def _get_score_range(self, score: float) -> str:
        """Categorize score into range"""
        if score < 20:
            return "very_low"
        elif score < 40:
            return "low"
        elif score < 60:
            return "average"
        elif score < 80:
            return "high"
        else:
            return "very_high"

    # ── Export Methods ──────────────────────────────────────────────────────

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analytics report"""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "overview": self.get_assessment_comparison(),
            "big_five": self.get_big_five_stats(),
            "disc": self.get_disc_stats(),
            "trends": {
                "last_24h": self.get_assessments_last_24h(),
                "last_7d": self.get_assessments_last_7d(),
                "time_series_30d": self.get_time_series_data(30)
            },
            "users": self.get_user_demographics_by_type(),
            "conversion": self.get_completion_funnel()
        }
