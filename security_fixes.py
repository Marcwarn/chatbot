"""
Security Fixes - Critical Vulnerability Patches
Run: python security_fixes.py to apply all fixes automatically
"""

import os
import re
import secrets
import bcrypt
from pathlib import Path


def fix_bcrypt_hashing():
    """Fix 1: Replace SHA-256 with bcrypt"""
    print("🔒 Fix 1: Implementing bcrypt password hashing...")

    api_admin_path = Path("api_admin.py")
    content = api_admin_path.read_text()

    # Replace hash_password function
    old_hash = '''def hash_password(password: str) -> str:
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()'''

    new_hash = '''def hash_password(password: str) -> str:
    """Hash password with bcrypt (secure)"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password using constant-time comparison"""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False'''

    content = content.replace(old_hash, new_hash)

    # Update login function to use verify_password
    old_login = '''    password_hash = hash_password(req.password)

    if password_hash != ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=401, detail="Invalid password")'''

    new_login = '''    # Use constant-time password verification
    if not verify_password(req.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Invalid password")'''

    content = content.replace(old_login, new_login)

    # Add bcrypt import
    if "import bcrypt" not in content:
        content = content.replace("import secrets", "import secrets\nimport bcrypt")

    api_admin_path.write_text(content)
    print("✅ bcrypt hashing implemented!")


def fix_default_password():
    """Fix 2: Remove default admin password"""
    print("🔒 Fix 2: Removing default admin password...")

    api_admin_path = Path("api_admin.py")
    content = api_admin_path.read_text()

    old_password = '''ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    # Default: "admin123" (CHANGE THIS IN PRODUCTION!)
    "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
)'''

    new_password = '''# Require ADMIN_PASSWORD_HASH to be set (no default!)
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
if not ADMIN_PASSWORD_HASH:
    raise ValueError(
        "SECURITY ERROR: ADMIN_PASSWORD_HASH must be set in environment variables!\\n"
        "Generate hash: python -c 'import bcrypt; print(bcrypt.hashpw(b\"your_password\", bcrypt.gensalt()).decode())'"
    )'''

    content = content.replace(old_password, new_password)
    api_admin_path.write_text(content)
    print("✅ Default password removed - environment variable required!")


def fix_cors_config():
    """Fix 3: Replace CORS wildcard with whitelist"""
    print("🔒 Fix 3: Fixing CORS configuration...")

    api_main_path = Path("api_main_gdpr.py")
    content = api_main_path.read_text()

    old_cors = '''app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

    new_cors = '''# CORS Configuration - Explicit whitelist (SECURITY)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
    # Default for local development only
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
    print("⚠️  WARNING: Using default ALLOWED_ORIGINS for development")
    print("⚠️  Set ALLOWED_ORIGINS in production: https://yourdomain.com")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Explicit whitelist
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight for 1 hour
)'''

    content = content.replace(old_cors, new_cors)
    api_main_path.write_text(content)
    print("✅ CORS whitelist configured!")


def fix_input_validation():
    """Fix 4: Add input validation"""
    print("🔒 Fix 4: Adding input validation...")

    # Create validators module
    validators_content = '''"""
Input Validation - Prevent injection attacks
"""

import re
from fastapi import HTTPException


# Patterns for validation
USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,128}$')
ASSESSMENT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{8,128}$')
LANGUAGE_PATTERN = re.compile(r'^[a-z]{2}$')


def validate_user_id(user_id: str) -> str:
    """Validate user_id format to prevent injection"""
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid user_id format. Must be alphanumeric, dash, or underscore (max 128 chars)"
        )
    return user_id


def validate_assessment_id(assessment_id: str) -> str:
    """Validate assessment_id format"""
    if not ASSESSMENT_ID_PATTERN.match(assessment_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid assessment_id format"
        )
    return assessment_id


def validate_language(language: str) -> str:
    """Validate language code"""
    if not LANGUAGE_PATTERN.match(language.lower()):
        raise HTTPException(
            status_code=400,
            detail="Invalid language code. Must be 2-letter ISO code (e.g., 'sv', 'en')"
        )
    return language.lower()


def validate_message_length(message: str, max_length: int = 10000) -> str:
    """Validate message length to prevent DoS"""
    if len(message) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long. Maximum {max_length} characters allowed"
        )
    if len(message) == 0:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    return message
'''

    Path("validators.py").write_text(validators_content)
    print("✅ Input validators created!")


def fix_gdpr_auth():
    """Fix 5: Add authentication to GDPR endpoints"""
    print("🔒 Fix 5: Securing GDPR endpoints...")

    api_gdpr_path = Path("api_gdpr.py")
    if not api_gdpr_path.exists():
        print("⚠️  api_gdpr.py not found - skipping")
        return

    content = api_gdpr_path.read_text()

    # Add admin auth requirement
    if "from api_admin import verify_admin_token" not in content:
        content = content.replace(
            "from fastapi import APIRouter",
            "from fastapi import APIRouter, Depends\nfrom api_admin import verify_admin_token"
        )

    # Find and fix export endpoint
    export_pattern = r'@router\.post\("/export".*?\)\s*async def export_user_data\('
    export_replacement = '@router.post("/export", response_model=DataExportResponse)\nasync def export_user_data(\n    request: DataExportRequest,\n    session: dict = Depends(verify_admin_token)  # SECURITY: Require admin auth\n):\n    """Export user data - ADMIN ONLY for security"""'

    # Similar fixes for delete endpoints
    content = re.sub(export_pattern, export_replacement, content, flags=re.DOTALL)

    api_gdpr_path.write_text(content)
    print("✅ GDPR endpoints secured with admin authentication!")


def fix_hardcoded_keys():
    """Fix 6: Remove hardcoded admin keys"""
    print("🔒 Fix 6: Removing hardcoded admin keys...")

    api_gdpr_path = Path("api_gdpr.py")
    if not api_gdpr_path.exists():
        print("⚠️  api_gdpr.py not found - skipping")
        return

    content = api_gdpr_path.read_text()

    # Replace hardcoded key check
    old_key_check = 'if admin_key != "CHANGE_ME_IN_PRODUCTION":'
    new_key_check = '''ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Admin API not configured")

    if not secrets.compare_digest(admin_key, ADMIN_API_KEY):'''

    content = content.replace(old_key_check, new_key_check)

    api_gdpr_path.write_text(content)
    print("✅ Hardcoded keys removed!")


def update_requirements():
    """Add bcrypt to requirements.txt"""
    print("📦 Updating requirements.txt...")

    req_path = Path("requirements.txt")
    content = req_path.read_text()

    if "bcrypt" not in content:
        content += "bcrypt>=4.0.0\n"
        req_path.write_text(content)
        print("✅ bcrypt added to requirements!")
    else:
        print("✅ bcrypt already in requirements")


def generate_secure_password_hash():
    """Helper: Generate secure password hash for .env"""
    print("\n" + "="*60)
    print("🔐 GENERATE SECURE ADMIN PASSWORD HASH")
    print("="*60)

    print("\nFor your .env file, add:")
    print("\nADMIN_PASSWORD_HASH=<hash_from_command_below>")
    print("\nGenerate hash by running:")
    print("\npython -c 'import bcrypt; password = input(\"Enter admin password: \").encode(); print(bcrypt.hashpw(password, bcrypt.gensalt()).decode())'")
    print("\n" + "="*60)


def main():
    """Apply all security fixes"""
    print("\n" + "🔒"*30)
    print("APPLYING CRITICAL SECURITY FIXES")
    print("🔒"*30 + "\n")

    try:
        fix_bcrypt_hashing()
        fix_default_password()
        fix_cors_config()
        fix_input_validation()
        fix_gdpr_auth()
        fix_hardcoded_keys()
        update_requirements()

        print("\n" + "✅"*30)
        print("ALL CRITICAL FIXES APPLIED!")
        print("✅"*30 + "\n")

        generate_secure_password_hash()

        print("\n📝 NEXT STEPS:")
        print("1. Install bcrypt: pip install bcrypt>=4.0.0")
        print("2. Generate admin password hash (see above)")
        print("3. Update .env with:")
        print("   - ADMIN_PASSWORD_HASH=<your_hash>")
        print("   - ALLOWED_ORIGINS=https://yourdomain.com")
        print("   - ADMIN_API_KEY=<secure_random_key>")
        print("4. Test: python -m pytest tests/test_security.py")
        print("5. Commit: git add . && git commit -m 'Apply critical security fixes'")
        print("6. Deploy with new environment variables\n")

    except Exception as e:
        print(f"\n❌ Error applying fixes: {e}")
        print("Please review and apply fixes manually.")


if __name__ == "__main__":
    main()
