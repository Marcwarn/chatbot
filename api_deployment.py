"""
Deployment Information API
Provides real-time deployment status, URL, and health using Vercel API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import requests

router = APIRouter(prefix="/api/v1/deployment", tags=["deployment"])


class DeploymentInfo(BaseModel):
    """Current deployment information"""
    environment: str  # "production", "preview", "development", "local"
    deployment_url: Optional[str] = None
    deployment_id: Optional[str] = None
    state: Optional[str] = None  # "READY", "ERROR", "BUILDING", etc.
    created_at: Optional[str] = None
    ready_at: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    branch: Optional[str] = None
    vercel_connected: bool = False


class HealthStatus(BaseModel):
    """Deployment health status"""
    status: str  # "HEALTHY", "WARNING", "DEGRADED", "UNKNOWN"
    deployment_count: int
    success_rate: float
    failed_deployments: int
    avg_build_time_seconds: Optional[float] = None
    warnings: List[str] = []
    issues: List[str] = []
    timestamp: str


def get_vercel_token() -> Optional[str]:
    """Get Vercel token from environment"""
    return os.getenv("VERCEL_TOKEN")


def get_current_environment() -> str:
    """Detect current deployment environment"""
    # Vercel automatically sets these environment variables
    vercel_env = os.getenv("VERCEL_ENV")  # "production", "preview", or "development"

    if vercel_env:
        return vercel_env

    # Fallback detection
    if os.getenv("VERCEL"):
        return "vercel"

    return "local"


def fetch_latest_deployment() -> Optional[Dict[str, Any]]:
    """Fetch latest deployment info from Vercel API"""
    token = get_vercel_token()

    if not token:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Fetch recent deployments
        url = "https://api.vercel.com/v6/deployments"
        params = {"limit": 1}  # Get only the latest

        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        deployments = data.get("deployments", [])

        if deployments:
            return deployments[0]

        return None

    except Exception as e:
        print(f"Error fetching Vercel deployment: {e}")
        return None


def fetch_deployment_health() -> Optional[Dict[str, Any]]:
    """Fetch deployment health statistics from Vercel API"""
    token = get_vercel_token()

    if not token:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Fetch recent deployments for health check
        url = "https://api.vercel.com/v6/deployments"
        params = {"limit": 10}  # Last 10 deployments

        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        deployments = data.get("deployments", [])

        if not deployments:
            return None

        # Calculate health metrics
        total = len(deployments)
        successful = sum(1 for d in deployments if d.get("state") == "READY")
        failed = sum(1 for d in deployments if d.get("state") == "ERROR")
        building = sum(1 for d in deployments if d.get("state") == "BUILDING")

        success_rate = (successful / total * 100) if total > 0 else 0

        # Calculate average build time
        build_times = []
        for d in deployments:
            created = d.get("createdAt", 0)
            ready = d.get("ready", 0)
            if ready and created:
                build_time = (ready - created) / 1000  # Convert to seconds
                build_times.append(build_time)

        avg_build_time = sum(build_times) / len(build_times) if build_times else None

        # Determine health status
        warnings = []
        issues = []

        if failed > 0:
            issues.append(f"{failed} deployment(s) failed")

        if building > 0:
            warnings.append(f"{building} deployment(s) still building")

        if avg_build_time and avg_build_time > 60:
            warnings.append(f"Slow average build time: {avg_build_time:.1f}s")

        if failed > 0:
            health_status = "DEGRADED"
        elif len(warnings) > 2:
            health_status = "WARNING"
        else:
            health_status = "HEALTHY"

        return {
            "status": health_status,
            "deployment_count": total,
            "success_rate": round(success_rate, 2),
            "failed_deployments": failed,
            "avg_build_time_seconds": round(avg_build_time, 2) if avg_build_time else None,
            "warnings": warnings,
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"Error fetching deployment health: {e}")
        return None


@router.get("/info", response_model=DeploymentInfo)
async def get_deployment_info():
    """
    Get current deployment information

    Returns deployment URL, environment, state, and commit info.
    Works both locally and on Vercel.
    """
    environment = get_current_environment()

    # Try to get info from Vercel environment variables first (fastest)
    vercel_url = os.getenv("VERCEL_URL")
    vercel_deployment_id = os.getenv("VERCEL_DEPLOYMENT_ID")
    vercel_git_commit_sha = os.getenv("VERCEL_GIT_COMMIT_SHA")
    vercel_git_commit_message = os.getenv("VERCEL_GIT_COMMIT_MESSAGE")
    vercel_git_branch = os.getenv("VERCEL_GIT_COMMIT_REF")

    # If running on Vercel, we have env vars
    if vercel_url:
        deployment_url = f"https://{vercel_url}" if not vercel_url.startswith("http") else vercel_url

        return DeploymentInfo(
            environment=environment,
            deployment_url=deployment_url,
            deployment_id=vercel_deployment_id,
            state="READY",  # If we're running, we're ready
            commit_sha=vercel_git_commit_sha[:7] if vercel_git_commit_sha else None,
            commit_message=vercel_git_commit_message,
            branch=vercel_git_branch,
            vercel_connected=True
        )

    # If local, try to fetch latest deployment from API
    token = get_vercel_token()

    if not token:
        return DeploymentInfo(
            environment=environment,
            deployment_url="http://localhost:8000" if environment == "local" else None,
            vercel_connected=False
        )

    # Fetch from Vercel API
    deployment = fetch_latest_deployment()

    if deployment:
        created_at = deployment.get("createdAt", 0)
        ready_at = deployment.get("ready", 0)

        return DeploymentInfo(
            environment=environment,
            deployment_url=f"https://{deployment.get('url')}" if deployment.get('url') else None,
            deployment_id=deployment.get("uid"),
            state=deployment.get("state"),
            created_at=datetime.fromtimestamp(created_at / 1000).isoformat() if created_at else None,
            ready_at=datetime.fromtimestamp(ready_at / 1000).isoformat() if ready_at else None,
            commit_sha=deployment.get("meta", {}).get("githubCommitSha", "")[:7],
            commit_message=deployment.get("meta", {}).get("githubCommitMessage"),
            branch=deployment.get("meta", {}).get("githubCommitRef"),
            vercel_connected=True
        )

    return DeploymentInfo(
        environment=environment,
        deployment_url="http://localhost:8000" if environment == "local" else None,
        vercel_connected=False
    )


@router.get("/health", response_model=HealthStatus)
async def get_deployment_health():
    """
    Get deployment health status

    Analyzes recent deployments and provides health metrics.
    Requires VERCEL_TOKEN to be set.
    """
    token = get_vercel_token()

    if not token:
        raise HTTPException(
            status_code=503,
            detail="VERCEL_TOKEN not configured - health monitoring unavailable"
        )

    health = fetch_deployment_health()

    if not health:
        return HealthStatus(
            status="UNKNOWN",
            deployment_count=0,
            success_rate=0,
            failed_deployments=0,
            warnings=["Unable to fetch deployment data from Vercel API"],
            timestamp=datetime.utcnow().isoformat()
        )

    return HealthStatus(**health)


@router.get("/status")
async def get_deployment_status():
    """
    Quick deployment status check

    Returns simplified deployment status for monitoring.
    """
    environment = get_current_environment()
    vercel_url = os.getenv("VERCEL_URL")
    vercel_connected = get_vercel_token() is not None

    return {
        "status": "operational",
        "environment": environment,
        "url": f"https://{vercel_url}" if vercel_url else "http://localhost:8000",
        "vercel_connected": vercel_connected,
        "timestamp": datetime.utcnow().isoformat()
    }
