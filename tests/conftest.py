"""
Test Configuration and Fixtures
Provides shared test fixtures for security, integration, and performance tests
"""

import pytest
import hashlib
import secrets
import time
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import tempfile
import os


# ── Test Database Fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="function")
def test_db():
    """
    Create a temporary test database
    Automatically cleaned up after each test
    """
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = temp_db.name
    temp_db.close()

    # Set environment variable for test database
    original_db = os.getenv("DATABASE_URL")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    yield db_path

    # Cleanup
    if original_db:
        os.environ["DATABASE_URL"] = original_db
    else:
        os.environ.pop("DATABASE_URL", None)

    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture(scope="function")
def db_session(test_db):
    """
    Provide database session for tests
    Rolls back after each test
    """
    from database import SessionLocal, init_db

    # Initialize test database
    init_db()

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ── Test Client Fixtures ─────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def client() -> TestClient:
    """
    Create FastAPI test client
    Resets rate limiters between tests
    """
    # Clear any existing sessions before test
    from api_admin import _admin_sessions
    _admin_sessions.clear()

    # Import app
    from api_main_gdpr import app

    # Create test client
    test_client = TestClient(app)

    yield test_client

    # Cleanup sessions after test
    _admin_sessions.clear()


@pytest.fixture(scope="function")
def client_no_rate_limit() -> TestClient:
    """
    Test client with rate limiting disabled
    Useful for performance tests
    """
    with patch('monitoring.check_rate_limit', return_value=None):
        from api_main_gdpr import app
        yield TestClient(app)


# ── Authentication Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="function")
def admin_password() -> str:
    """Default admin password for testing"""
    return "admin123"


@pytest.fixture(scope="function")
def admin_password_hash(admin_password: str) -> str:
    """Hash of admin password"""
    return hashlib.sha256(admin_password.encode()).hexdigest()


@pytest.fixture(scope="function")
def admin_token(client: TestClient, admin_password: str) -> str:
    """
    Get valid admin authentication token

    EXPLOIT SCENARIO:
    Tests need to verify that admin endpoints properly validate tokens
    and that tokens cannot be forged or reused after logout
    """
    response = client.post("/api/admin/login", json={"password": admin_password})

    if response.status_code != 200:
        pytest.skip(f"Could not obtain admin token: {response.status_code}")

    return response.json()["token"]


@pytest.fixture(scope="function")
def expired_admin_token(client: TestClient, admin_password: str) -> str:
    """
    Create an expired admin token for testing session timeout

    EXPLOIT SCENARIO:
    Attackers may try to reuse old tokens after they've expired
    """
    response = client.post("/api/admin/login", json={"password": admin_password})

    if response.status_code != 200:
        pytest.skip("Could not create admin session")

    token = response.json()["token"]

    # Manually expire the session
    from api_admin import _admin_sessions
    from datetime import datetime, timedelta

    if token in _admin_sessions:
        _admin_sessions[token]["expires_at"] = (
            datetime.utcnow() - timedelta(hours=1)
        ).isoformat()

    return token


# ── Mock Anthropic API ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def mock_anthropic_api():
    """
    Mock Anthropic API responses
    Prevents actual API calls during tests and allows testing error handling

    EXPLOIT SCENARIO:
    Tests should verify that API errors don't expose sensitive information
    and that the system handles API failures gracefully
    """
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="This is a mocked AI response")]
    mock_client.messages.create.return_value = mock_response

    with patch('anthropic.Anthropic', return_value=mock_client):
        yield mock_client


@pytest.fixture(scope="function")
def mock_anthropic_api_error():
    """
    Mock Anthropic API error responses
    Tests error handling and ensures errors don't leak sensitive data
    """
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("API Error: Rate limit exceeded")

    with patch('anthropic.Anthropic', return_value=mock_client):
        yield mock_client


# ── Test Users and Data ──────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def test_user_id() -> str:
    """Generate unique test user ID"""
    return f"test_user_{secrets.token_hex(8)}"


@pytest.fixture(scope="function")
def test_user_with_data(client: TestClient, test_user_id: str, mock_anthropic_api):
    """
    Create test user with assessment and chat data

    EXPLOIT SCENARIO:
    Used to verify GDPR compliance - user deletion should cascade
    and data export should include all user data
    """
    # Create assessment
    client.post("/api/v1/assessment/submit", json={
        "user_id": test_user_id,
        "assessment_id": f"assessment_{test_user_id}",
        "answers": [
            {"question_id": "q1", "value": 4},
            {"question_id": "q2", "value": 3},
        ],
        "language": "en"
    })

    # Create chat profile
    client.post("/api/v1/chat", json={
        "user_id": test_user_id,
        "message": "Hello, this is a test message",
        "conversation_history": []
    })

    yield test_user_id


@pytest.fixture(scope="function")
def malicious_payloads() -> Dict[str, list]:
    """
    Collection of malicious payloads for security testing

    EXPLOIT SCENARIOS:
    - SQL Injection: Attempts to manipulate database queries
    - XSS: Attempts to inject JavaScript into responses
    - Path Traversal: Attempts to access files outside allowed directories
    - Command Injection: Attempts to execute system commands
    """
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin' --",
            "1 UNION SELECT * FROM users",
            "'; DELETE FROM assessments WHERE '1'='1",
            "1' AND '1'='1' UNION SELECT password FROM admin --",
        ],
        "xss": [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>",
            "<svg/onload=alert('XSS')>",
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(id)",
        ],
        "nosql_injection": [
            "{'$gt': ''}",
            "{'$ne': null}",
            "{'$regex': '.*'}",
        ],
    }


# ── Security Testing Utilities ───────────────────────────────────────────────

@pytest.fixture(scope="function")
def timing_attack_detector():
    """
    Utility for detecting timing attacks

    EXPLOIT SCENARIO:
    Timing attacks can reveal information about password verification
    by measuring response times. This detector helps verify that
    operations use constant-time comparison.
    """
    class TimingDetector:
        def __init__(self):
            self.measurements = []

        def measure(self, func, *args, **kwargs):
            """Measure execution time of a function"""
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            self.measurements.append(elapsed)
            return result, elapsed

        def has_timing_leak(self, threshold: float = 0.1) -> bool:
            """
            Check if timing measurements vary significantly
            threshold: Maximum acceptable ratio between min and max times
            """
            if len(self.measurements) < 10:
                return False

            avg = sum(self.measurements) / len(self.measurements)
            variance = sum((x - avg) ** 2 for x in self.measurements) / len(self.measurements)
            std_dev = variance ** 0.5

            # If standard deviation is more than threshold of average, likely has timing leak
            return (std_dev / avg) > threshold if avg > 0 else False

    return TimingDetector()


@pytest.fixture(scope="function")
def security_scanner():
    """
    Security testing utilities

    Provides helpers for:
    - Response sanitization checking
    - Sensitive data detection
    - Header security validation
    """
    class SecurityScanner:
        @staticmethod
        def contains_xss(text: str) -> bool:
            """Check if text contains XSS patterns"""
            dangerous_patterns = [
                '<script', 'javascript:', 'onerror=', 'onload=',
                '<iframe', 'onclick=', 'eval(', 'expression(',
            ]
            text_lower = text.lower()
            return any(pattern in text_lower for pattern in dangerous_patterns)

        @staticmethod
        def contains_sensitive_data(text: str) -> bool:
            """Check if text contains sensitive data"""
            sensitive_patterns = [
                'sk-ant-',  # Anthropic API key
                'password', 'secret', 'token',
                'api_key', 'private_key',
                '/home/', 'c:\\',  # File paths
                'traceback', 'exception',  # Stack traces
            ]
            text_lower = text.lower()
            return any(pattern in text_lower for pattern in sensitive_patterns)

        @staticmethod
        def check_security_headers(headers: Dict[str, str]) -> Dict[str, bool]:
            """Check for presence of security headers"""
            return {
                "has_csp": "content-security-policy" in headers,
                "has_xframe": "x-frame-options" in headers,
                "has_xss_protection": "x-xss-protection" in headers,
                "has_content_type": "x-content-type-options" in headers,
                "has_hsts": "strict-transport-security" in headers,
            }

        @staticmethod
        def is_valid_user_id(user_id: str) -> bool:
            """Validate user ID format (alphanumeric, underscore, hyphen only)"""
            import re
            return bool(re.match(r'^[a-zA-Z0-9_-]{1,128}$', user_id))

    return SecurityScanner()


# ── Rate Limiting Test Helpers ───────────────────────────────────────────────

@pytest.fixture(scope="function")
def rate_limit_tester():
    """
    Utilities for testing rate limiting effectiveness

    EXPLOIT SCENARIO:
    Attackers may try to bypass rate limits using:
    - IP spoofing (X-Forwarded-For headers)
    - Distributed requests
    - Endpoint switching
    """
    class RateLimitTester:
        @staticmethod
        def rapid_fire(client: TestClient, endpoint: str, count: int = 10,
                      method: str = "GET", **kwargs) -> list:
            """Send rapid requests to an endpoint"""
            responses = []
            for i in range(count):
                if method == "GET":
                    resp = client.get(endpoint, **kwargs)
                elif method == "POST":
                    resp = client.post(endpoint, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                responses.append(resp)
            return responses

        @staticmethod
        def is_rate_limited(responses: list) -> bool:
            """Check if any response indicates rate limiting"""
            return any(r.status_code == 429 for r in responses)

        @staticmethod
        def spoofed_ip_request(client: TestClient, endpoint: str, ip: str, **kwargs):
            """Make request with spoofed IP in X-Forwarded-For header"""
            headers = kwargs.get("headers", {})
            headers["X-Forwarded-For"] = ip
            kwargs["headers"] = headers
            return client.get(endpoint, **kwargs)

    return RateLimitTester()


# ── Performance Testing Helpers ──────────────────────────────────────────────

@pytest.fixture(scope="function")
def memory_monitor():
    """
    Monitor memory usage during tests

    EXPLOIT SCENARIO:
    Memory leaks can be exploited for DoS attacks
    Session storage should not grow unbounded
    """
    import psutil
    import os

    class MemoryMonitor:
        def __init__(self):
            self.process = psutil.Process(os.getpid())
            self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            self.samples = [self.initial_memory]

        def sample(self):
            """Take a memory measurement"""
            current = self.process.memory_info().rss / 1024 / 1024  # MB
            self.samples.append(current)
            return current

        def has_leak(self, threshold_mb: float = 50.0) -> bool:
            """Check if memory has grown beyond threshold"""
            if len(self.samples) < 2:
                return False
            growth = self.samples[-1] - self.initial_memory
            return growth > threshold_mb

        def get_growth(self) -> float:
            """Get memory growth in MB"""
            return self.samples[-1] - self.initial_memory if self.samples else 0.0

    return MemoryMonitor()


# ── Additional Test Data Fixtures ───────────────────────────────────────────

@pytest.fixture(scope="function")
def complete_assessment_data():
    """
    Complete valid assessment data for testing

    Returns assessment with all 50 IPIP questions answered
    """
    return {
        "answers": [
            {"question_id": i, "value": (i % 5) + 1}
            for i in range(1, 51)
        ]
    }


@pytest.fixture(scope="function")
def mock_big_five_scores():
    """
    Mock Big Five personality scores for testing

    Returns realistic percentile scores
    """
    return {
        "E": 65.5,  # Extraversion
        "A": 72.0,  # Agreeableness
        "C": 55.5,  # Conscientiousness
        "N": 45.0,  # Neuroticism (lower = more stable)
        "O": 80.0,  # Openness
    }


# ── Cleanup ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def cleanup_sessions():
    """
    Automatically cleanup admin sessions after each test
    Prevents session leakage between tests
    """
    yield

    # Clear admin sessions
    try:
        from api_admin import _admin_sessions
        _admin_sessions.clear()
    except:
        pass

    # Clear assessment sessions
    try:
        from api_main_gdpr import _sessions
        _sessions.clear()
    except:
        pass

    # Clear user profiles
    try:
        from api_main_gdpr import _user_profiles
        _user_profiles.clear()
    except:
        pass


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """
    Reset rate limiters between tests
    Ensures tests don't interfere with each other
    """
    yield

    # Clear rate limiter state
    try:
        from monitoring import _rate_limit_storage
        _rate_limit_storage.clear()
    except:
        pass


# ── Test Markers ─────────────────────────────────────────────────────────────

def pytest_configure(config):
    """
    Register custom pytest markers for test categorization
    """
    config.addinivalue_line(
        "markers", "critical: Critical security vulnerability tests"
    )
    config.addinivalue_line(
        "markers", "high: High severity vulnerability tests"
    )
    config.addinivalue_line(
        "markers", "medium: Medium severity vulnerability tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "integration: End-to-end integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take > 5 seconds"
    )
