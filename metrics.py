"""
Security Metrics and Analytics
Track security events, generate reports, and calculate security scores
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path


# ── Security Metrics Tracker ─────────────────────────────────────────────────

class SecurityMetricsTracker:
    """
    Track and analyze security metrics over time
    """

    def __init__(self):
        self.metrics_history: List[Dict] = []
        self.daily_summaries: Dict[str, Dict] = {}

    def record_metric(
        self,
        metric_type: str,
        value: int,
        metadata: Dict = None
    ):
        """Record a security metric"""
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": metric_type,
            "value": value,
            "metadata": metadata or {}
        }

        self.metrics_history.append(metric)

        # Keep only last 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        self.metrics_history = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Get metrics summary for last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

        # Aggregate by type
        summary = defaultdict(lambda: {"count": 0, "total_value": 0})

        for metric in recent_metrics:
            metric_type = metric["type"]
            summary[metric_type]["count"] += 1
            summary[metric_type]["total_value"] += metric["value"]

        return dict(summary)

    def get_timeline(
        self,
        metric_type: str,
        hours: int = 24,
        interval_minutes: int = 60
    ) -> Dict:
        """
        Get timeline data for a specific metric type
        Returns data suitable for charting
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        now = datetime.utcnow()

        # Create time buckets
        buckets = []
        labels = []

        current = cutoff
        while current <= now:
            buckets.append({
                "start": current,
                "end": current + timedelta(minutes=interval_minutes),
                "count": 0
            })
            labels.append(current.strftime("%H:%M"))
            current += timedelta(minutes=interval_minutes)

        # Fill buckets with data
        for metric in self.metrics_history:
            if metric["type"] != metric_type:
                continue

            timestamp = datetime.fromisoformat(metric["timestamp"])
            if timestamp < cutoff:
                continue

            for bucket in buckets:
                if bucket["start"] <= timestamp < bucket["end"]:
                    bucket["count"] += metric["value"]
                    break

        return {
            "labels": labels,
            "values": [b["count"] for b in buckets]
        }


# ── Security Score Calculator ────────────────────────────────────────────────

class SecurityScoreCalculator:
    """
    Calculate overall security score based on metrics
    Score: 0-100 (100 = perfect, 0 = critical issues)
    """

    def __init__(self):
        # Weight factors for different event types
        self.weights = {
            "sql_injection": -10,      # Very serious
            "xss_attempt": -8,          # Serious
            "brute_force": -5,          # Concerning
            "data_exfiltration": -15,   # Critical
            "dos_attempt": -3,          # Moderate
            "scanner_detected": -2,     # Minor
            "honeypot_triggered": -4,   # Concerning
            "suspicious_pattern": -1,   # Low impact
        }

    def calculate_score(self, events: List[Dict], hours: int = 24) -> Dict:
        """
        Calculate security score based on recent events
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Filter recent events
        recent_events = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        # Start with perfect score
        base_score = 100

        # Deduct points for each event
        deductions = defaultdict(int)
        total_deduction = 0

        for event in recent_events:
            event_type = event.get("event_type", "")
            weight = self.weights.get(event_type, -1)

            deductions[event_type] += abs(weight)
            total_deduction += abs(weight)

        # Calculate final score
        final_score = max(0, base_score - total_deduction)

        # Determine grade
        grade = self._get_grade(final_score)

        # Calculate trend (compare to previous period)
        previous_cutoff = cutoff - timedelta(hours=hours)
        previous_events = [
            e for e in events
            if previous_cutoff <= datetime.fromisoformat(e["timestamp"]) < cutoff
        ]

        previous_deduction = sum(
            abs(self.weights.get(e.get("event_type", ""), -1))
            for e in previous_events
        )

        trend = "improving" if previous_deduction > total_deduction else \
                "degrading" if previous_deduction < total_deduction else \
                "stable"

        return {
            "score": final_score,
            "grade": grade,
            "total_events": len(recent_events),
            "deductions": dict(deductions),
            "trend": trend,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


# ── Attack Pattern Analyzer ──────────────────────────────────────────────────

class AttackPatternAnalyzer:
    """
    Analyze attack patterns to identify trends and sophisticated attacks
    """

    def analyze_patterns(self, events: List[Dict], hours: int = 24) -> Dict:
        """
        Analyze attack patterns in recent events
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        recent_events = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        if not recent_events:
            return {
                "patterns_detected": [],
                "risk_level": "low",
                "recommendations": []
            }

        patterns = []

        # Pattern 1: Coordinated attack (multiple attack types from same IP)
        ip_attacks = defaultdict(set)
        for event in recent_events:
            ip = event.get("client_ip", "unknown")
            event_type = event.get("event_type", "")
            ip_attacks[ip].add(event_type)

        for ip, attack_types in ip_attacks.items():
            if len(attack_types) >= 3:
                patterns.append({
                    "type": "coordinated_attack",
                    "severity": "high",
                    "description": f"IP {ip} attempted {len(attack_types)} different attack types",
                    "ip": ip,
                    "attack_types": list(attack_types)
                })

        # Pattern 2: Distributed attack (same attack type from multiple IPs)
        attack_ips = defaultdict(set)
        for event in recent_events:
            event_type = event.get("event_type", "")
            ip = event.get("client_ip", "unknown")
            attack_ips[event_type].add(ip)

        for attack_type, ips in attack_ips.items():
            if len(ips) >= 5:
                patterns.append({
                    "type": "distributed_attack",
                    "severity": "high",
                    "description": f"{attack_type} from {len(ips)} different IPs (possible DDoS)",
                    "attack_type": attack_type,
                    "ip_count": len(ips)
                })

        # Pattern 3: Reconnaissance (scanner detected + subsequent attacks)
        scanner_ips = set()
        attack_ips_set = set()

        for event in recent_events:
            ip = event.get("client_ip", "unknown")
            if event.get("event_type") == "scanner_detected":
                scanner_ips.add(ip)
            else:
                attack_ips_set.add(ip)

        reconnaissance_ips = scanner_ips & attack_ips_set
        if reconnaissance_ips:
            patterns.append({
                "type": "reconnaissance_to_attack",
                "severity": "critical",
                "description": f"{len(reconnaissance_ips)} IPs performed reconnaissance then attacked",
                "ips": list(reconnaissance_ips)
            })

        # Pattern 4: Persistent attacker (same IP over extended period)
        ip_timeline = defaultdict(list)
        for event in recent_events:
            ip = event.get("client_ip", "unknown")
            timestamp = datetime.fromisoformat(event["timestamp"])
            ip_timeline[ip].append(timestamp)

        for ip, timestamps in ip_timeline.items():
            if len(timestamps) >= 10:
                time_span = max(timestamps) - min(timestamps)
                if time_span.total_seconds() > 3600:  # More than 1 hour
                    patterns.append({
                        "type": "persistent_attacker",
                        "severity": "medium",
                        "description": f"IP {ip} has been attacking for {time_span.total_seconds()/3600:.1f} hours",
                        "ip": ip,
                        "event_count": len(timestamps)
                    })

        # Determine overall risk level
        risk_level = "low"
        if any(p["severity"] == "critical" for p in patterns):
            risk_level = "critical"
        elif any(p["severity"] == "high" for p in patterns):
            risk_level = "high"
        elif patterns:
            risk_level = "medium"

        # Generate recommendations
        recommendations = self._generate_recommendations(patterns)

        return {
            "patterns_detected": patterns,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    def _generate_recommendations(self, patterns: List[Dict]) -> List[str]:
        """Generate recommendations based on detected patterns"""
        recommendations = []

        pattern_types = [p["type"] for p in patterns]

        if "coordinated_attack" in pattern_types:
            recommendations.append(
                "Consider implementing more aggressive IP blocking for coordinated attacks"
            )

        if "distributed_attack" in pattern_types:
            recommendations.append(
                "Implement rate limiting at CDN/WAF level to mitigate DDoS"
            )

        if "reconnaissance_to_attack" in pattern_types:
            recommendations.append(
                "Auto-block IPs detected scanning within 24 hours"
            )

        if "persistent_attacker" in pattern_types:
            recommendations.append(
                "Review firewall rules and consider permanent IP blocks"
            )

        if not recommendations:
            recommendations.append(
                "Continue monitoring. Current security posture is adequate."
            )

        return recommendations


# ── Weekly Report Generator ──────────────────────────────────────────────────

class WeeklySecurityReportGenerator:
    """
    Generate comprehensive weekly security reports
    """

    def __init__(self):
        self.score_calculator = SecurityScoreCalculator()
        self.pattern_analyzer = AttackPatternAnalyzer()

    def generate_report(self, events: List[Dict]) -> str:
        """Generate weekly security report"""
        # Get last 7 days of events
        cutoff = datetime.utcnow() - timedelta(days=7)

        weekly_events = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        # Calculate statistics
        event_counts = defaultdict(int)
        unique_ips = set()
        endpoints_attacked = defaultdict(int)

        for event in weekly_events:
            event_counts[event.get("event_type", "unknown")] += 1
            unique_ips.add(event.get("client_ip", "unknown"))
            endpoints_attacked[event.get("endpoint", "unknown")] += 1

        # Get security score
        score_data = self.score_calculator.calculate_score(events, hours=168)  # 7 days

        # Analyze patterns
        patterns = self.pattern_analyzer.analyze_patterns(events, hours=168)

        # Generate report
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                      WEEKLY SECURITY REPORT                                ║
║                 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│ SECURITY SCORE                                                           │
└─────────────────────────────────────────────────────────────────────────┘

  Overall Score: {score_data['score']}/100 (Grade: {score_data['grade']})
  Trend:         {score_data['trend'].upper()}
  Total Events:  {score_data['total_events']}

┌─────────────────────────────────────────────────────────────────────────┐
│ ATTACK SUMMARY                                                           │
└─────────────────────────────────────────────────────────────────────────┘

  Total Security Events:    {len(weekly_events)}
  Unique Attacker IPs:      {len(unique_ips)}
  Endpoints Targeted:       {len(endpoints_attacked)}

  Events by Type:
"""

        for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"    • {event_type.replace('_', ' ').title()}: {count}\n"

        report += f"""
┌─────────────────────────────────────────────────────────────────────────┐
│ MOST TARGETED ENDPOINTS                                                  │
└─────────────────────────────────────────────────────────────────────────┘

"""

        for endpoint, count in sorted(endpoints_attacked.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"    {count:4d} attempts  →  {endpoint}\n"

        report += f"""
┌─────────────────────────────────────────────────────────────────────────┐
│ ATTACK PATTERNS DETECTED                                                 │
└─────────────────────────────────────────────────────────────────────────┘

  Risk Level: {patterns['risk_level'].upper()}
  Patterns:   {len(patterns['patterns_detected'])} detected

"""

        if patterns['patterns_detected']:
            for pattern in patterns['patterns_detected']:
                report += f"  ⚠️  {pattern['type'].upper()} ({pattern['severity']})\n"
                report += f"      {pattern['description']}\n\n"
        else:
            report += "  ✅ No sophisticated attack patterns detected\n\n"

        report += f"""
┌─────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATIONS                                                          │
└─────────────────────────────────────────────────────────────────────────┘

"""

        for i, rec in enumerate(patterns['recommendations'], 1):
            report += f"  {i}. {rec}\n"

        report += f"""
┌─────────────────────────────────────────────────────────────────────────┐
│ TOP ATTACKING IPS                                                        │
└─────────────────────────────────────────────────────────────────────────┘

"""

        # Count events per IP
        ip_counts = defaultdict(int)
        for event in weekly_events:
            ip_counts[event.get("client_ip", "unknown")] += 1

        for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"    {ip:20s}  {count:4d} events\n"

        report += """
╔═══════════════════════════════════════════════════════════════════════════╗
║                         END OF REPORT                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

        return report

    def save_report(self, report: str) -> str:
        """Save report to file"""
        reports_dir = Path("security_reports")
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = reports_dir / f"weekly_report_{timestamp}.txt"

        filename.write_text(report)

        return str(filename)


# ── Export Metrics to JSON ───────────────────────────────────────────────────

class MetricsExporter:
    """Export metrics in various formats"""

    @staticmethod
    def export_to_json(
        events: List[Dict],
        score_data: Dict,
        patterns: Dict,
        filename: str = None
    ) -> str:
        """Export metrics to JSON"""
        export_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "security_score": score_data,
            "attack_patterns": patterns,
            "event_summary": {
                "total_events": len(events),
                "events_by_type": {}
            }
        }

        # Count events by type
        for event in events:
            event_type = event.get("event_type", "unknown")
            export_data["event_summary"]["events_by_type"][event_type] = \
                export_data["event_summary"]["events_by_type"].get(event_type, 0) + 1

        if filename:
            Path(filename).write_text(json.dumps(export_data, indent=2))
            return filename
        else:
            return json.dumps(export_data, indent=2)


# ── Global Instances ──────────────────────────────────────────────────────────

metrics_tracker = SecurityMetricsTracker()
score_calculator = SecurityScoreCalculator()
pattern_analyzer = AttackPatternAnalyzer()
report_generator = WeeklySecurityReportGenerator()
metrics_exporter = MetricsExporter()
