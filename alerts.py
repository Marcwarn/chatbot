"""
Security Alerts and Incident Response System
Sends notifications via Slack/email and manages auto-blocking
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime
import httpx
import sentry_sdk
from enum import Enum


# ── Alert Severity Levels ────────────────────────────────────────────────────

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Alert Channels ───────────────────────────────────────────────────────────

class SlackAlerter:
    """Send security alerts to Slack"""

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        details: Dict = None
    ) -> bool:
        """Send alert to Slack"""
        if not self.enabled:
            print(f"⚠️  Slack not configured - Alert: {title}")
            return False

        # Color based on severity
        colors = {
            AlertSeverity.LOW: "#36a64f",      # Green
            AlertSeverity.MEDIUM: "#ff9900",   # Orange
            AlertSeverity.HIGH: "#ff6600",     # Dark orange
            AlertSeverity.CRITICAL: "#ff0000"  # Red
        }

        # Build Slack message
        payload = {
            "username": "Security Monitor",
            "icon_emoji": ":shield:",
            "attachments": [{
                "color": colors.get(severity, "#ff9900"),
                "title": f"🚨 {title}",
                "text": message,
                "fields": [
                    {
                        "title": "Severity",
                        "value": severity.value.upper(),
                        "short": True
                    },
                    {
                        "title": "Timestamp",
                        "value": datetime.utcnow().isoformat(),
                        "short": True
                    }
                ],
                "footer": "Security Monitoring System",
                "ts": int(datetime.utcnow().timestamp())
            }]
        }

        # Add details if provided
        if details:
            for key, value in details.items():
                payload["attachments"][0]["fields"].append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": True
                })

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"❌ Failed to send Slack alert: {e}")
            return False


class EmailAlerter:
    """Send security alerts via email"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("ALERT_FROM_EMAIL", self.smtp_user)
        self.to_emails = os.getenv("ALERT_TO_EMAILS", "").split(",")

        self.enabled = all([
            self.smtp_host,
            self.smtp_user,
            self.smtp_password,
            self.to_emails
        ])

    def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        details: Dict = None
    ) -> bool:
        """Send alert via email"""
        if not self.enabled:
            print(f"⚠️  Email not configured - Alert: {title}")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{severity.value.upper()}] {title}"
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)

            # Build email body
            text_body = f"""
Security Alert - {severity.value.upper()}

{title}

{message}

Timestamp: {datetime.utcnow().isoformat()}
"""

            if details:
                text_body += "\nDetails:\n"
                for key, value in details.items():
                    text_body += f"- {key.replace('_', ' ').title()}: {value}\n"

            html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .alert-box {{
            border-left: 4px solid {'#ff0000' if severity == AlertSeverity.CRITICAL else '#ff9900'};
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .severity {{
            color: {'#ff0000' if severity == AlertSeverity.CRITICAL else '#ff9900'};
            font-weight: bold;
        }}
        .details {{
            margin-top: 15px;
            padding: 10px;
            background-color: #fff;
            border: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="alert-box">
        <h2>🚨 Security Alert</h2>
        <p class="severity">Severity: {severity.value.upper()}</p>
        <h3>{title}</h3>
        <p>{message}</p>
        <p><small>Timestamp: {datetime.utcnow().isoformat()}</small></p>
"""

            if details:
                html_body += '<div class="details"><h4>Details:</h4><ul>'
                for key, value in details.items():
                    html_body += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
                html_body += "</ul></div>"

            html_body += """
    </div>
</body>
</html>
"""

            # Attach parts
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"❌ Failed to send email alert: {e}")
            return False


class SentryAlerter:
    """Send critical alerts to Sentry"""

    def __init__(self):
        self.enabled = bool(os.getenv("SENTRY_DSN"))

    def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        details: Dict = None
    ) -> bool:
        """Send critical alerts to Sentry"""
        if not self.enabled:
            return False

        try:
            # Map severity to Sentry level
            sentry_levels = {
                AlertSeverity.LOW: "info",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.HIGH: "error",
                AlertSeverity.CRITICAL: "fatal"
            }

            level = sentry_levels.get(severity, "warning")

            # Send to Sentry
            with sentry_sdk.push_scope() as scope:
                scope.set_context("security_alert", {
                    "title": title,
                    "message": message,
                    "severity": severity.value,
                    **(details or {})
                })

                sentry_sdk.capture_message(
                    f"Security Alert: {title}",
                    level=level
                )

            return True

        except Exception as e:
            print(f"❌ Failed to send Sentry alert: {e}")
            return False


# ── Incident Report Generator ────────────────────────────────────────────────

class IncidentReportGenerator:
    """Generate detailed incident reports"""

    @staticmethod
    def generate_report(
        incident_type: str,
        client_ip: str,
        endpoint: str,
        events: List[Dict],
        blocked: bool = False
    ) -> str:
        """Generate incident report"""
        report = f"""
════════════════════════════════════════════════════════════════
SECURITY INCIDENT REPORT
════════════════════════════════════════════════════════════════

Incident Type: {incident_type}
Timestamp:     {datetime.utcnow().isoformat()}
Client IP:     {client_ip}
Endpoint:      {endpoint}
Status:        {'BLOCKED' if blocked else 'DETECTED'}

────────────────────────────────────────────────────────────────
EVENT TIMELINE
────────────────────────────────────────────────────────────────
"""

        for i, event in enumerate(events, 1):
            report += f"""
Event {i}:
  Time:       {event.get('timestamp', 'N/A')}
  Type:       {event.get('event_type', 'N/A')}
  Details:    {json.dumps(event.get('details', {}), indent=14)}
"""

        report += """
────────────────────────────────────────────────────────────────
RECOMMENDED ACTIONS
────────────────────────────────────────────────────────────────
"""

        # Add recommendations based on incident type
        recommendations = {
            "brute_force": [
                "Review login attempt patterns",
                "Consider implementing CAPTCHA",
                "Verify IP is not legitimate user"
            ],
            "sql_injection": [
                "Verify input validation is working",
                "Review database query logs",
                "Consider WAF rules update"
            ],
            "xss_attempt": [
                "Check output encoding",
                "Review CSP headers",
                "Verify input sanitization"
            ],
            "dos_attempt": [
                "Monitor server resources",
                "Consider rate limit adjustments",
                "Review traffic patterns"
            ],
            "scanner_detected": [
                "Verify block is in place",
                "Check for data exfiltration",
                "Review access logs"
            ]
        }

        for rec in recommendations.get(incident_type, ["Investigate further"]):
            report += f"• {rec}\n"

        report += """
════════════════════════════════════════════════════════════════
"""

        return report

    @staticmethod
    def save_report(report: str, incident_id: str) -> str:
        """Save incident report to file"""
        import os
        from pathlib import Path

        # Create reports directory
        reports_dir = Path("security_reports")
        reports_dir.mkdir(exist_ok=True)

        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = reports_dir / f"incident_{incident_id}_{timestamp}.txt"

        # Save report
        filename.write_text(report)

        return str(filename)


# ── Alert Manager ────────────────────────────────────────────────────────────

class AlertManager:
    """
    Central alert management system
    Coordinates alerts across multiple channels
    """

    def __init__(self):
        self.slack = SlackAlerter()
        self.email = EmailAlerter()
        self.sentry = SentryAlerter()
        self.report_generator = IncidentReportGenerator()

        # Alert thresholds
        self.alert_thresholds = {
            "brute_force": AlertSeverity.HIGH,
            "sql_injection": AlertSeverity.CRITICAL,
            "xss_attempt": AlertSeverity.HIGH,
            "dos_attempt": AlertSeverity.MEDIUM,
            "data_exfiltration": AlertSeverity.CRITICAL,
            "scanner_detected": AlertSeverity.MEDIUM,
            "honeypot_triggered": AlertSeverity.HIGH,
            "suspicious_pattern": AlertSeverity.LOW,
        }

    async def send_security_alert(
        self,
        event_type: str,
        client_ip: str,
        endpoint: str,
        details: Dict = None,
        auto_blocked: bool = False
    ):
        """
        Send security alert through appropriate channels
        """
        # Determine severity
        severity = self.alert_thresholds.get(event_type, AlertSeverity.MEDIUM)

        # Build alert message
        title = f"Security Event: {event_type.replace('_', ' ').title()}"
        message = f"Detected {event_type} from IP {client_ip} on endpoint {endpoint}"

        if auto_blocked:
            message += " (IP automatically blocked)"

        # Prepare alert details
        alert_details = {
            "client_ip": client_ip,
            "endpoint": endpoint,
            "event_type": event_type,
            "blocked": "Yes" if auto_blocked else "No",
            **(details or {})
        }

        # Send through appropriate channels based on severity
        if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            # Send to all channels for high/critical
            await self.slack.send_alert(title, message, severity, alert_details)
            self.email.send_alert(title, message, severity, alert_details)
            self.sentry.send_alert(title, message, severity, alert_details)

            # Generate incident report for critical events
            if severity == AlertSeverity.CRITICAL:
                report = self.report_generator.generate_report(
                    event_type, client_ip, endpoint,
                    [{"timestamp": datetime.utcnow().isoformat(), "event_type": event_type, "details": details}],
                    auto_blocked
                )
                incident_id = f"{event_type}_{client_ip.replace('.', '_')}"
                report_path = self.report_generator.save_report(report, incident_id)
                print(f"📝 Incident report saved: {report_path}")

        elif severity == AlertSeverity.MEDIUM:
            # Send to Slack and Sentry
            await self.slack.send_alert(title, message, severity, alert_details)
            self.sentry.send_alert(title, message, severity, alert_details)

        else:
            # Low severity - just log to Sentry
            self.sentry.send_alert(title, message, severity, alert_details)

        print(f"🚨 Alert sent: [{severity.value.upper()}] {title}")

    async def send_daily_summary(self, security_events: List[Dict]):
        """Send daily security summary"""
        if not security_events:
            return

        # Count events by type
        event_counts = {}
        for event in security_events:
            event_type = event.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Build summary
        title = "Daily Security Summary"
        message = f"Total security events in last 24 hours: {len(security_events)}"

        details = {
            "total_events": len(security_events),
            **event_counts
        }

        # Send summary
        await self.slack.send_alert(title, message, AlertSeverity.LOW, details)


# ── Auto-blocking Manager ─────────────────────────────────────────────────────

class AutoBlockManager:
    """
    Manages automatic IP blocking based on security events
    """

    def __init__(self):
        self.block_rules = {
            "brute_force": {"duration": 3600, "threshold": 5},       # 1 hour after 5 attempts
            "sql_injection": {"duration": 86400, "threshold": 1},    # 24 hours after 1 attempt
            "xss_attempt": {"duration": 86400, "threshold": 1},      # 24 hours after 1 attempt
            "dos_attempt": {"duration": 1800, "threshold": 1},       # 30 min after detection
            "scanner_detected": {"duration": 7200, "threshold": 1},  # 2 hours
            "honeypot_triggered": {"duration": 7200, "threshold": 1}, # 2 hours
        }

    def should_block(self, event_type: str, event_count: int = 1) -> Dict:
        """Determine if IP should be blocked"""
        rule = self.block_rules.get(event_type)

        if not rule:
            return {"should_block": False, "duration": 0}

        should_block = event_count >= rule["threshold"]

        return {
            "should_block": should_block,
            "duration": rule["duration"],
            "reason": f"{event_type} threshold exceeded ({event_count}/{rule['threshold']})"
        }


# ── Global Alert Manager Instance ────────────────────────────────────────────

alert_manager = AlertManager()
auto_block_manager = AutoBlockManager()
