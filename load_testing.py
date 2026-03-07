"""
Load Testing Suite for Personality Assessment API
Simulates high-concurrency scenarios to identify bottlenecks and breaking points
"""

import asyncio
import httpx
import time
import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor
import random


# ============================================================================
# CONFIGURATION
# ============================================================================

TEST_CONFIG = {
    "base_url": "http://localhost:8000",  # Change to your API URL
    "concurrent_users": 1000,
    "test_duration_seconds": 60,
    "ramp_up_seconds": 10,  # Gradually increase load
}

# Test scenarios
SCENARIOS = {
    "assessment_flow": {
        "weight": 0.5,  # 50% of traffic
        "description": "Complete assessment (start -> submit)"
    },
    "chat": {
        "weight": 0.3,  # 30% of traffic
        "description": "Send chat messages"
    },
    "gdpr_export": {
        "weight": 0.1,  # 10% of traffic
        "description": "Export user data"
    },
    "admin_stats": {
        "weight": 0.1,  # 10% of traffic
        "description": "View admin dashboard"
    }
}


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

def generate_test_answers() -> List[Dict[str, int]]:
    """Generate random but valid assessment answers"""
    return [
        {"question_id": i + 1, "value": random.randint(1, 5)}
        for i in range(50)
    ]


def generate_test_chat_message() -> str:
    """Generate random chat message"""
    messages = [
        "Vad passar min profil för yrke?",
        "Hur kan jag utveckla min ledarskapsförmåga?",
        "Ge mig råd om karriär",
        "Vad säger min profil om mina styrkor?",
        "Hur kan jag bli bättre på att samarbeta?",
    ]
    return random.choice(messages)


# ============================================================================
# PERFORMANCE METRICS COLLECTOR
# ============================================================================

class MetricsCollector:
    """Collects and aggregates performance metrics"""

    def __init__(self):
        self.requests: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None

    def record_request(self, endpoint: str, duration_ms: float,
                      status_code: int, success: bool):
        """Record a request"""
        self.requests.append({
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "success": success,
            "timestamp": time.time()
        })

    def record_error(self, endpoint: str, error: str):
        """Record an error"""
        self.errors.append({
            "endpoint": endpoint,
            "error": error,
            "timestamp": time.time()
        })

    def get_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not self.requests:
            return {"error": "No requests recorded"}

        durations = [r["duration_ms"] for r in self.requests]
        successes = [r for r in self.requests if r["success"]]
        failures = [r for r in self.requests if not r["success"]]

        total_duration = self.end_time - self.start_time if self.end_time else 0

        # Group by endpoint
        by_endpoint = {}
        for req in self.requests:
            ep = req["endpoint"]
            if ep not in by_endpoint:
                by_endpoint[ep] = []
            by_endpoint[ep].append(req["duration_ms"])

        endpoint_stats = {
            ep: {
                "count": len(times),
                "avg_ms": statistics.mean(times),
                "p50_ms": statistics.median(times),
                "p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0],
                "p99_ms": sorted(times)[int(len(times) * 0.99)] if len(times) > 1 else times[0],
                "min_ms": min(times),
                "max_ms": max(times),
            }
            for ep, times in by_endpoint.items()
        }

        return {
            "total_requests": len(self.requests),
            "successful_requests": len(successes),
            "failed_requests": len(failures),
            "success_rate": len(successes) / len(self.requests) * 100,
            "error_count": len(self.errors),
            "total_duration_seconds": total_duration,
            "requests_per_second": len(self.requests) / total_duration if total_duration > 0 else 0,
            "avg_response_time_ms": statistics.mean(durations),
            "median_response_time_ms": statistics.median(durations),
            "p95_response_time_ms": sorted(durations)[int(len(durations) * 0.95)],
            "p99_response_time_ms": sorted(durations)[int(len(durations) * 0.99)],
            "min_response_time_ms": min(durations),
            "max_response_time_ms": max(durations),
            "by_endpoint": endpoint_stats,
            "errors": self.errors[:10]  # First 10 errors
        }


# ============================================================================
# TEST SCENARIOS
# ============================================================================

async def scenario_assessment_flow(client: httpx.AsyncClient,
                                   metrics: MetricsCollector,
                                   user_id: str):
    """Test complete assessment flow"""

    # 1. Start assessment
    start_time = time.time()
    try:
        response = await client.post(
            "/api/v1/assessment/start",
            json={
                "user_id": user_id,
                "language": "sv",
                "consent_data_processing": True,
                "consent_analysis": True,
                "consent_storage": True
            },
            timeout=30.0
        )
        duration_ms = (time.time() - start_time) * 1000
        success = response.status_code == 200
        metrics.record_request("/api/v1/assessment/start", duration_ms,
                              response.status_code, success)

        if not success:
            metrics.record_error("/api/v1/assessment/start",
                               f"Status {response.status_code}")
            return

        data = response.json()
        assessment_id = data["assessment_id"]

    except Exception as e:
        metrics.record_error("/api/v1/assessment/start", str(e))
        return

    # 2. Submit assessment
    start_time = time.time()
    try:
        response = await client.post(
            "/api/v1/assessment/submit",
            json={
                "assessment_id": assessment_id,
                "answers": generate_test_answers()
            },
            timeout=30.0
        )
        duration_ms = (time.time() - start_time) * 1000
        success = response.status_code == 200
        metrics.record_request("/api/v1/assessment/submit", duration_ms,
                              response.status_code, success)

        if not success:
            metrics.record_error("/api/v1/assessment/submit",
                               f"Status {response.status_code}")

    except Exception as e:
        metrics.record_error("/api/v1/assessment/submit", str(e))


async def scenario_chat(client: httpx.AsyncClient,
                       metrics: MetricsCollector,
                       user_id: str):
    """Test chat functionality"""

    start_time = time.time()
    try:
        response = await client.post(
            "/api/v1/chat",
            json={
                "user_id": user_id,
                "message": generate_test_chat_message(),
                "conversation_history": [],
                "include_profile": False  # Don't require profile for load test
            },
            timeout=30.0
        )
        duration_ms = (time.time() - start_time) * 1000
        success = response.status_code == 200
        metrics.record_request("/api/v1/chat", duration_ms,
                              response.status_code, success)

        if not success:
            metrics.record_error("/api/v1/chat", f"Status {response.status_code}")

    except Exception as e:
        metrics.record_error("/api/v1/chat", str(e))


async def scenario_gdpr_export(client: httpx.AsyncClient,
                               metrics: MetricsCollector,
                               user_id: str):
    """Test GDPR data export"""

    start_time = time.time()
    try:
        response = await client.post(
            "/api/v1/gdpr/export",
            json={"user_id": user_id},
            timeout=30.0
        )
        duration_ms = (time.time() - start_time) * 1000
        success = response.status_code == 200
        metrics.record_request("/api/v1/gdpr/export", duration_ms,
                              response.status_code, success)

        if not success:
            metrics.record_error("/api/v1/gdpr/export",
                               f"Status {response.status_code}")

    except Exception as e:
        metrics.record_error("/api/v1/gdpr/export", str(e))


async def scenario_health_check(client: httpx.AsyncClient,
                                metrics: MetricsCollector):
    """Test health check endpoint"""

    start_time = time.time()
    try:
        response = await client.get("/api/v1/health", timeout=10.0)
        duration_ms = (time.time() - start_time) * 1000
        success = response.status_code == 200
        metrics.record_request("/api/v1/health", duration_ms,
                              response.status_code, success)

    except Exception as e:
        metrics.record_error("/api/v1/health", str(e))


# ============================================================================
# VIRTUAL USER
# ============================================================================

async def virtual_user(user_id: int, metrics: MetricsCollector,
                      base_url: str, duration_seconds: int):
    """
    Simulates a single user performing random actions

    Each virtual user:
    - Runs for specified duration
    - Picks random scenarios based on weights
    - Records all metrics
    """

    user_identifier = f"loadtest_user_{user_id}"

    async with httpx.AsyncClient(base_url=base_url) as client:
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            # Pick random scenario based on weights
            rand = random.random()
            cumulative = 0

            scenario = None
            for name, config in SCENARIOS.items():
                cumulative += config["weight"]
                if rand <= cumulative:
                    scenario = name
                    break

            # Execute scenario
            try:
                if scenario == "assessment_flow":
                    await scenario_assessment_flow(client, metrics, user_identifier)
                elif scenario == "chat":
                    await scenario_chat(client, metrics, user_identifier)
                elif scenario == "gdpr_export":
                    await scenario_gdpr_export(client, metrics, user_identifier)
                elif scenario == "admin_stats":
                    await scenario_health_check(client, metrics)

            except Exception as e:
                metrics.record_error("virtual_user", str(e))

            # Small delay between requests (0.5-2 seconds)
            await asyncio.sleep(random.uniform(0.5, 2.0))


# ============================================================================
# LOAD TEST ORCHESTRATOR
# ============================================================================

async def run_load_test(base_url: str = None,
                       concurrent_users: int = 100,
                       duration_seconds: int = 60,
                       ramp_up_seconds: int = 10):
    """
    Run complete load test

    Args:
        base_url: API base URL
        concurrent_users: Number of concurrent virtual users
        duration_seconds: Test duration
        ramp_up_seconds: Time to gradually increase load
    """

    base_url = base_url or TEST_CONFIG["base_url"]

    print("=" * 70)
    print("LOAD TEST STARTING")
    print("=" * 70)
    print(f"Base URL: {base_url}")
    print(f"Concurrent Users: {concurrent_users}")
    print(f"Duration: {duration_seconds}s")
    print(f"Ramp-up: {ramp_up_seconds}s")
    print("=" * 70)

    metrics = MetricsCollector()
    metrics.start_time = time.time()

    # Create virtual users with ramp-up
    tasks = []
    users_per_second = concurrent_users / ramp_up_seconds

    for i in range(concurrent_users):
        # Calculate delay for ramp-up
        delay = (i / users_per_second) if ramp_up_seconds > 0 else 0

        # Create task with delay
        task = asyncio.create_task(
            delayed_start(
                virtual_user(i, metrics, base_url, duration_seconds),
                delay
            )
        )
        tasks.append(task)

    print(f"\n🚀 Spawning {concurrent_users} virtual users...")

    # Wait for all users to complete
    await asyncio.gather(*tasks, return_exceptions=True)

    metrics.end_time = time.time()

    print("\n✅ Load test complete!")
    print("=" * 70)

    return metrics.get_summary()


async def delayed_start(coro, delay: float):
    """Helper to delay task start (for ramp-up)"""
    await asyncio.sleep(delay)
    return await coro


# ============================================================================
# RATE LIMIT TESTING
# ============================================================================

async def test_rate_limits(base_url: str = None):
    """
    Test rate limiting behavior under load

    Sends rapid requests to trigger rate limits
    """

    base_url = base_url or TEST_CONFIG["base_url"]

    print("\n" + "=" * 70)
    print("RATE LIMIT TEST")
    print("=" * 70)

    metrics = MetricsCollector()
    metrics.start_time = time.time()

    async with httpx.AsyncClient(base_url=base_url) as client:
        # Send 200 rapid requests to /api/v1/health
        tasks = []
        for i in range(200):
            task = asyncio.create_task(
                scenario_health_check(client, metrics)
            )
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    metrics.end_time = time.time()

    summary = metrics.get_summary()

    print(f"\nTotal requests: {summary['total_requests']}")
    print(f"Successful: {summary['successful_requests']}")
    print(f"Rate limited (429): {summary['failed_requests']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")

    # Check if any 429 responses
    rate_limited = sum(1 for r in metrics.requests if r['status_code'] == 429)
    print(f"\n{'✅' if rate_limited > 0 else '❌'} Rate limiting {'is' if rate_limited > 0 else 'NOT'} working")
    print(f"   Rate limited requests: {rate_limited}")

    return summary


# ============================================================================
# DATABASE PERFORMANCE TEST
# ============================================================================

async def test_database_performance(base_url: str = None):
    """
    Test database query performance under concurrent load

    Simulates many concurrent database operations
    """

    base_url = base_url or TEST_CONFIG["base_url"]

    print("\n" + "=" * 70)
    print("DATABASE PERFORMANCE TEST")
    print("=" * 70)

    metrics = MetricsCollector()
    metrics.start_time = time.time()

    # Create 100 concurrent assessment flows (heavy DB usage)
    async with httpx.AsyncClient(base_url=base_url) as client:
        tasks = []
        for i in range(100):
            task = asyncio.create_task(
                scenario_assessment_flow(client, metrics, f"dbtest_user_{i}")
            )
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    metrics.end_time = time.time()

    summary = metrics.get_summary()

    print(f"\nTotal DB operations: {summary['total_requests']}")
    print(f"Average response time: {summary['avg_response_time_ms']:.0f}ms")
    print(f"P95 response time: {summary['p95_response_time_ms']:.0f}ms")
    print(f"P99 response time: {summary['p99_response_time_ms']:.0f}ms")
    print(f"Success rate: {summary['success_rate']:.1f}%")

    # Performance assessment
    avg_ms = summary['avg_response_time_ms']
    if avg_ms < 100:
        print("\n✅ EXCELLENT database performance (<100ms avg)")
    elif avg_ms < 500:
        print("\n✅ GOOD database performance (<500ms avg)")
    elif avg_ms < 1000:
        print("\n⚠️  ACCEPTABLE database performance (<1s avg)")
    else:
        print("\n❌ POOR database performance (>1s avg) - optimization needed!")

    return summary


# ============================================================================
# REPORT GENERATOR
# ============================================================================

def generate_report(results: Dict[str, Any], filename: str = "load_test_report.json"):
    """Generate JSON report of test results"""

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "test_config": TEST_CONFIG,
        "results": results
    }

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {filename}")


def print_summary(summary: Dict[str, Any]):
    """Print formatted summary"""

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    print(f"\n📊 Overall Performance:")
    print(f"   Total Requests: {summary['total_requests']}")
    print(f"   Successful: {summary['successful_requests']}")
    print(f"   Failed: {summary['failed_requests']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Requests/sec: {summary['requests_per_second']:.1f}")

    print(f"\n⏱️  Response Times:")
    print(f"   Average: {summary['avg_response_time_ms']:.0f}ms")
    print(f"   Median: {summary['median_response_time_ms']:.0f}ms")
    print(f"   P95: {summary['p95_response_time_ms']:.0f}ms")
    print(f"   P99: {summary['p99_response_time_ms']:.0f}ms")
    print(f"   Min: {summary['min_response_time_ms']:.0f}ms")
    print(f"   Max: {summary['max_response_time_ms']:.0f}ms")

    print(f"\n🎯 By Endpoint:")
    for endpoint, stats in summary['by_endpoint'].items():
        print(f"   {endpoint}:")
        print(f"      Requests: {stats['count']}")
        print(f"      Avg: {stats['avg_ms']:.0f}ms | P95: {stats['p95_ms']:.0f}ms | P99: {stats['p99_ms']:.0f}ms")

    if summary['errors']:
        print(f"\n❌ Errors ({summary['error_count']} total):")
        for error in summary['errors'][:5]:
            print(f"   - {error['endpoint']}: {error['error']}")

    print("\n" + "=" * 70)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Run all load tests"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                  PERSONALITY API LOAD TESTING                    ║
║                                                                  ║
║  This will simulate high-concurrency scenarios to identify      ║
║  performance bottlenecks and system breaking points.            ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Rate limiting
    print("\n[1/3] Testing rate limits...")
    await test_rate_limits()

    # Test 2: Database performance
    print("\n[2/3] Testing database performance...")
    await test_database_performance()

    # Test 3: Full load test
    print("\n[3/3] Running full load test...")
    summary = await run_load_test(
        concurrent_users=100,  # Start with 100, increase as needed
        duration_seconds=30,
        ramp_up_seconds=10
    )

    # Print summary
    print_summary(summary)

    # Generate report
    generate_report(summary, "load_test_report.json")

    print("\n✅ All load tests complete!")


if __name__ == "__main__":
    # Run load tests
    asyncio.run(main())
