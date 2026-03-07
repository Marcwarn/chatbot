"""
Smoke tests - Quick validation after deployment
"""
import requests
import sys
import argparse

def test_api_health(base_url):
    """Test API health endpoint"""
    response = requests.get(f"{base_url}/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_landing_page(base_url):
    """Test landing page loads"""
    response = requests.get(base_url)
    assert response.status_code == 200
    assert "Upptäck Din Personlighet" in response.text

def test_big_five_page(base_url):
    """Test Big Five assessment page"""
    response = requests.get(f"{base_url}/big-five-demo.html")
    assert response.status_code == 200

def test_disc_page(base_url):
    """Test DISC assessment page"""
    response = requests.get(f"{base_url}/disc-assessment.html")
    assert response.status_code == 200

def test_admin_login(base_url):
    """Test admin login endpoint exists"""
    response = requests.post(
        f"{base_url}/api/admin/login",
        json={"password": "test"}
    )
    # Should return 401 (not 500 or 404)
    assert response.status_code == 401

def run_smoke_tests(base_url, critical_only=False):
    """Run all smoke tests"""
    tests = [
        ("API Health", test_api_health),
        ("Landing Page", test_landing_page),
        ("Big Five Page", test_big_five_page),
        ("DISC Page", test_disc_page),
        ("Admin Login", test_admin_login),
    ]

    print(f"🧪 Running smoke tests on {base_url}...")

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func(base_url)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
            if critical_only and name in ["API Health", "Landing Page"]:
                print("Critical test failed!")
                sys.exit(1)

    print(f"\n📊 Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--critical-only", action="store_true")
    args = parser.parse_args()

    run_smoke_tests(args.url, args.critical_only)
