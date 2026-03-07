"""
Performance regression checker
Ensures performance metrics don't degrade between releases
"""
import json
import sys
import os

# Performance thresholds
THRESHOLDS = {
    "api_response_time_ms": 2000,  # Max 2 seconds
    "database_query_time_ms": 500,  # Max 500ms
    "memory_usage_mb": 512,  # Max 512MB
    "cpu_usage_percent": 80,  # Max 80%
}

def check_performance_regression():
    """Check if performance metrics are within acceptable limits"""

    # Check if performance report exists
    report_file = "performance_metrics.json"

    if not os.path.exists(report_file):
        print("⚠️  No performance metrics found. Skipping regression check.")
        return 0

    try:
        with open(report_file, 'r') as f:
            metrics = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load performance metrics: {e}")
        return 1

    failed = []
    passed = []

    for metric, threshold in THRESHOLDS.items():
        if metric in metrics:
            value = metrics[metric]
            if value > threshold:
                failed.append(f"{metric}: {value} > {threshold}")
            else:
                passed.append(f"{metric}: {value} ≤ {threshold}")

    print("\n📊 Performance Regression Check")
    print("=" * 50)

    if passed:
        print("\n✅ Passed:")
        for item in passed:
            print(f"  {item}")

    if failed:
        print("\n❌ Failed:")
        for item in failed:
            print(f"  {item}")
        print("\n⚠️  Performance regression detected!")
        return 1

    print("\n✅ All performance metrics within thresholds")
    return 0

if __name__ == "__main__":
    sys.exit(check_performance_regression())
