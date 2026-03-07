#!/usr/bin/env python3
"""
Security Monitoring Setup Script
Automates the setup and configuration of the security monitoring system
"""

import os
import sys
from pathlib import Path


def print_banner():
    """Print setup banner"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              🛡️  SECURITY MONITORING SETUP WIZARD  🛡️                    ║
║                                                                           ║
║  This script will help you set up comprehensive security monitoring      ║
║  for your application with real-time attack detection and alerting.      ║
║                                                                           ║
╚══════════════════════════════════════════════════════════════════════════╝
""")


def check_files():
    """Check if all required files exist"""
    print("\n📋 Checking required files...")

    required_files = [
        "monitoring.py",
        "alerts.py",
        "metrics.py",
        "api_security.py",
        "security_integration.py",
        "security_dashboard.html",
        "database.py"
    ]

    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (MISSING)")
            missing.append(file)

    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        return False

    print("\n✅ All required files present!")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")

    required_packages = [
        "fastapi",
        "sentry_sdk",
        "httpx",
        "bcrypt",
        "sqlalchemy"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (NOT INSTALLED)")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✅ All dependencies installed!")
    return True


def setup_database():
    """Initialize security database tables"""
    print("\n🗄️  Setting up database tables...")

    try:
        from database import db

        db.create_tables()
        print("  ✅ Security tables created successfully!")
        return True

    except Exception as e:
        print(f"  ❌ Failed to create tables: {e}")
        return False


def check_env_vars():
    """Check environment variables"""
    print("\n🔧 Checking environment configuration...")

    # Required
    required_vars = {
        "ADMIN_PASSWORD_HASH": "Admin password hash (bcrypt)"
    }

    # Optional but recommended
    optional_vars = {
        "SENTRY_DSN": "Sentry error tracking",
        "SLACK_WEBHOOK_URL": "Slack alerts",
        "SMTP_HOST": "Email alerts",
        "SMTP_USER": "Email sender",
        "SMTP_PASSWORD": "Email password"
    }

    missing_required = []
    missing_optional = []

    # Check required
    for var, desc in required_vars.items():
        if os.getenv(var):
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var} - {desc} (REQUIRED)")
            missing_required.append(var)

    # Check optional
    for var, desc in optional_vars.items():
        if os.getenv(var):
            print(f"  ✅ {var}")
        else:
            print(f"  ⚠️  {var} - {desc} (optional)")
            missing_optional.append(var)

    if missing_required:
        print(f"\n❌ Missing required variables: {', '.join(missing_required)}")
        print("\nTo generate ADMIN_PASSWORD_HASH:")
        print("python -c 'import bcrypt; password = input(\"Enter password: \").encode(); print(bcrypt.hashpw(password, bcrypt.gensalt()).decode())'")
        return False

    if missing_optional:
        print(f"\nℹ️  Optional variables not set: {', '.join(missing_optional)}")
        print("These features will be disabled but the system will still work.")

    return True


def create_example_env():
    """Create example .env file if it doesn't exist"""
    env_example = Path(".env.example")

    if env_example.exists():
        print("\n✅ .env.example already exists")
        return

    print("\n📝 Creating .env.example...")

    example_content = """# Security Monitoring Configuration

# Admin Authentication (REQUIRED)
ADMIN_PASSWORD_HASH=<generate-with-bcrypt>

# Sentry Error Tracking (Optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production

# Slack Alerts (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Alerts (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_FROM_EMAIL=security@yourdomain.com
ALERT_TO_EMAILS=admin@yourdomain.com,security@yourdomain.com

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Database (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///./assessment_gdpr.db
"""

    env_example.write_text(example_content)
    print("  ✅ Created .env.example")
    print("  ℹ️  Copy to .env and configure: cp .env.example .env")


def create_reports_directory():
    """Create security reports directory"""
    print("\n📁 Creating security reports directory...")

    reports_dir = Path("security_reports")
    reports_dir.mkdir(exist_ok=True)

    print("  ✅ Created security_reports/")


def test_import():
    """Test importing all security modules"""
    print("\n🧪 Testing module imports...")

    modules = [
        "monitoring",
        "alerts",
        "metrics",
        "api_security",
        "security_integration"
    ]

    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            failed.append(module)

    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        return False

    print("\n✅ All modules imported successfully!")
    return True


def print_next_steps():
    """Print next steps for user"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                          SETUP COMPLETE! 🎉                               ║
╚══════════════════════════════════════════════════════════════════════════╝

📝 NEXT STEPS:

1️⃣  Configure Environment Variables
   • Copy .env.example to .env
   • Generate ADMIN_PASSWORD_HASH:
     python -c 'import bcrypt; password = input("Password: ").encode(); print(bcrypt.hashpw(password, bcrypt.gensalt()).decode())'
   • Add to .env file

2️⃣  Integrate with Main API
   Add to api_main_gdpr.py:

   from api_security import router as security_router
   from monitoring import comprehensive_security_middleware

   app.include_router(security_router)
   app.middleware("http")(comprehensive_security_middleware)

3️⃣  Start Your Application
   uvicorn api_main_gdpr:app --reload

4️⃣  Access Security Dashboard
   http://localhost:8000/api/admin/security/dashboard

5️⃣  Configure Alerts (Optional)
   • Set up Slack webhook
   • Configure email SMTP
   • Add Sentry DSN

6️⃣  Test Security Features
   # Test alerts
   curl -X POST http://localhost:8000/api/admin/security/test-alert

   # View metrics
   curl http://localhost:8000/api/admin/security/metrics

📚 Documentation: SECURITY_MONITORING_GUIDE.md

🆘 Need Help?
   • Check security_reports/ for logs
   • Review Sentry for errors
   • Test individual endpoints

═══════════════════════════════════════════════════════════════════════════

🛡️  Your application now has enterprise-grade security monitoring!

═══════════════════════════════════════════════════════════════════════════
""")


def main():
    """Main setup function"""
    print_banner()

    # Run checks
    checks = [
        ("Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment", check_env_vars),
        ("Database", setup_database),
        ("Imports", test_import)
    ]

    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
            print(f"\n⚠️  {name} check failed!")

    # Create additional files
    create_example_env()
    create_reports_directory()

    # Print results
    if all_passed:
        print("\n" + "="*76)
        print("✅ ALL CHECKS PASSED!")
        print("="*76)
        print_next_steps()
        return 0
    else:
        print("\n" + "="*76)
        print("⚠️  SOME CHECKS FAILED")
        print("="*76)
        print("\nPlease fix the issues above and run again.")
        print("Setup will continue but some features may not work.\n")
        print_next_steps()
        return 1


if __name__ == "__main__":
    sys.exit(main())
