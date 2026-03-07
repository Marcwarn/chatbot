"""
Vercel Deployment Monitor
Tracks deployments, identifies issues, sends alerts
"""

import requests
import os
from datetime import datetime
from typing import List, Dict, Optional
import json
import sys


class VercelMonitor:
    """Monitor Vercel deployments"""

    def __init__(self, token: str, team_id: Optional[str] = None):
        self.token = token
        self.team_id = team_id
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get_deployments(self, limit: int = 10) -> List[Dict]:
        """Get recent deployments"""
        url = f"{self.base_url}/v6/deployments"
        params = {"limit": limit}
        if self.team_id:
            params["teamId"] = self.team_id

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get("deployments", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching deployments: {e}")
            return []

    def get_deployment_details(self, deployment_id: str) -> Dict:
        """Get detailed deployment info"""
        url = f"{self.base_url}/v13/deployments/{deployment_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching deployment details: {e}")
            return {}

    def get_build_logs(self, deployment_id: str) -> str:
        """Get build logs for deployment"""
        url = f"{self.base_url}/v1/deployments/{deployment_id}/events"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            events = response.json()
            logs = []
            for event in events:
                if event.get("type") == "stdout":
                    logs.append(event.get("payload", {}).get("text", ""))

            return "\n".join(logs)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching build logs: {e}")
            return ""

    def analyze_deployment(self, deployment: Dict) -> Dict:
        """Analyze deployment for issues"""
        issues = []
        warnings = []

        # Check state
        state = deployment.get("state", "UNKNOWN")
        if state == "ERROR":
            issues.append("Deployment failed")
        elif state == "BUILDING":
            warnings.append("Deployment still building")
        elif state == "QUEUED":
            warnings.append("Deployment queued")

        # Check build time
        created_at = deployment.get("createdAt", 0)
        ready_at = deployment.get("ready", 0)
        build_time = None

        if ready_at and created_at:
            build_time = (ready_at - created_at) / 1000  # Convert to seconds
            if build_time > 60:
                warnings.append(f"Slow build: {build_time:.1f}s")
            elif build_time > 120:
                issues.append(f"Very slow build: {build_time:.1f}s")

        # Format timestamps
        created_timestamp = datetime.fromtimestamp(created_at / 1000) if created_at else None
        ready_timestamp = datetime.fromtimestamp(ready_at / 1000) if ready_at else None

        return {
            "deployment_id": deployment.get("uid"),
            "url": deployment.get("url"),
            "state": state,
            "created_at": created_timestamp.isoformat() if created_timestamp else None,
            "ready_at": ready_timestamp.isoformat() if ready_timestamp else None,
            "build_time_seconds": round(build_time, 2) if build_time else None,
            "issues": issues,
            "warnings": warnings,
            "commit": deployment.get("meta", {}).get("githubCommitSha", "unknown")[:7]
        }

    def check_for_warnings(self, logs: str) -> List[str]:
        """Check logs for common warnings"""
        warnings = []

        if not logs:
            return warnings

        # Check for build warnings
        if "WARN!" in logs:
            warnings.append("Build warnings detected in logs")

        # Check for cache issues
        if "cache" in logs.lower() and "not available" in logs.lower():
            warnings.append("Build cache not available - add cacheDirectories to vercel.json")

        if "no files were prepared" in logs.lower():
            warnings.append("No files prepared for cache - check build configuration")

        # Check for builds override warning
        if "builds` existing in your configuration" in logs:
            warnings.append("vercel.json builds overriding dashboard settings")

        # Check for slow operations
        if "timeout" in logs.lower() or "timed out" in logs.lower():
            warnings.append("Timeout detected - increase function duration or optimize code")

        # Check for dependency issues
        if "error installing" in logs.lower() or "failed to install" in logs.lower():
            warnings.append("Dependency installation issues detected")

        return warnings

    def generate_report(self, detailed: bool = False) -> Dict:
        """Generate deployment health report"""
        deployments = self.get_deployments(limit=10)

        if not deployments:
            return {
                "error": "No deployments found or API error",
                "summary": {
                    "total_deployments": 0,
                    "successful": 0,
                    "failed": 0,
                    "success_rate": 0
                },
                "health_status": "UNKNOWN"
            }

        total = len(deployments)
        successful = sum(1 for d in deployments if d.get("state") == "READY")
        failed = sum(1 for d in deployments if d.get("state") == "ERROR")
        building = sum(1 for d in deployments if d.get("state") == "BUILDING")

        analyses = [self.analyze_deployment(d) for d in deployments]
        all_warnings = []
        all_issues = []

        # Collect warnings from logs if detailed report requested
        if detailed:
            for deployment in deployments[:3]:  # Check last 3 deployments
                deployment_id = deployment.get("uid")
                if deployment_id:
                    logs = self.get_build_logs(deployment_id)
                    log_warnings = self.check_for_warnings(logs)
                    all_warnings.extend(log_warnings)

        # Collect warnings and issues from analyses
        for analysis in analyses:
            all_warnings.extend(analysis["warnings"])
            all_issues.extend(analysis["issues"])

        # Remove duplicates while preserving order
        all_warnings = list(dict.fromkeys(all_warnings))
        all_issues = list(dict.fromkeys(all_issues))

        # Calculate average build time
        build_times = [a["build_time_seconds"] for a in analyses if a["build_time_seconds"]]
        avg_build_time = sum(build_times) / len(build_times) if build_times else 0

        # Determine health status
        if failed > 0:
            health_status = "DEGRADED"
        elif len(all_warnings) > 3:
            health_status = "WARNING"
        else:
            health_status = "HEALTHY"

        return {
            "summary": {
                "total_deployments": total,
                "successful": successful,
                "failed": failed,
                "building": building,
                "success_rate": round((successful / total * 100), 2) if total > 0 else 0,
                "avg_build_time_seconds": round(avg_build_time, 2)
            },
            "recent_deployments": analyses[:5],  # Show only 5 most recent
            "all_warnings": all_warnings,
            "all_issues": all_issues,
            "health_status": health_status,
            "timestamp": datetime.now().isoformat()
        }

    def print_report(self, report: Dict) -> None:
        """Print formatted report to console"""
        print("\n" + "="*60)
        print("VERCEL DEPLOYMENT HEALTH REPORT")
        print("="*60)

        if "error" in report:
            print(f"\n❌ ERROR: {report['error']}")
            return

        print(f"\n📊 Status: {report['health_status']}")
        print(f"🕐 Timestamp: {report['timestamp']}")

        summary = report['summary']
        print(f"\n📈 Summary:")
        print(f"   Total Deployments: {summary['total_deployments']}")
        print(f"   Successful: {summary['successful']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Building: {summary['building']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Avg Build Time: {summary['avg_build_time_seconds']:.2f}s")

        if report['all_issues']:
            print(f"\n❌ Issues ({len(report['all_issues'])}):")
            for issue in report['all_issues']:
                print(f"   - {issue}")

        if report['all_warnings']:
            print(f"\n⚠️  Warnings ({len(report['all_warnings'])}):")
            for warning in report['all_warnings']:
                print(f"   - {warning}")

        print(f"\n🚀 Recent Deployments:")
        for dep in report['recent_deployments']:
            status_icon = "✅" if dep['state'] == "READY" else "❌" if dep['state'] == "ERROR" else "🔄"
            print(f"   {status_icon} {dep['deployment_id'][:8]} - {dep['state']}")
            print(f"      URL: {dep['url']}")
            print(f"      Build Time: {dep['build_time_seconds']}s" if dep['build_time_seconds'] else "      Build Time: N/A")
            print(f"      Commit: {dep['commit']}")

        print("\n" + "="*60 + "\n")


def main():
    """Main entry point for monitoring script"""
    token = os.getenv("VERCEL_TOKEN")

    if not token:
        print("❌ ERROR: VERCEL_TOKEN environment variable not set")
        print("\nTo set up monitoring:")
        print("1. Get your token from: https://vercel.com/account/tokens")
        print("2. Export it: export VERCEL_TOKEN='your-token-here'")
        print("3. Run this script again")
        sys.exit(1)

    team_id = os.getenv("VERCEL_TEAM_ID")
    detailed = "--detailed" in sys.argv
    json_output = "--json" in sys.argv

    monitor = VercelMonitor(token, team_id)

    print("🔍 Checking Vercel deployments...")
    report = monitor.generate_report(detailed=detailed)

    if json_output:
        print(json.dumps(report, indent=2))
    else:
        monitor.print_report(report)

    # Exit with error code if degraded
    if report.get("health_status") == "DEGRADED":
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
