"""
GDPR-Compliant API Test Script
Tests all GDPR features including consent, export, delete, etc.
"""

import requests
import json
from typing import Dict

API_URL = "http://localhost:8000"

def print_header(text: str):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_response(response):
    """Pretty print response"""
    if response.status_code in [200, 201]:
        print(f"✅ Success ({response.status_code})")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Failed ({response.status_code})")
        print(response.text)

def test_gdpr_complete_flow():
    """Test complete GDPR-compliant flow"""

    print_header("🔒 GDPR-Compliant Assessment Flow Test")

    user_id = None
    assessment_id = None
    email = "test@example.com"

    # ========================================================================
    # STEP 1: Start Assessment with Consents
    # ========================================================================
    print_header("Step 1: Start Assessment (with GDPR Consents)")

    start_data = {
        "email": email,
        "assessment_type": "big_five",
        "language": "sv",
        "num_questions": 10,
        # GDPR: Required consents
        "consent_data_processing": True,
        "consent_ai_analysis": True,
        "consent_storage": True
    }

    print("📝 Request:")
    print(json.dumps(start_data, indent=2))

    response = requests.post(f"{API_URL}/api/v1/assessment/start", json=start_data)
    print_response(response)

    if response.status_code == 200:
        data = response.json()
        assessment_id = data["assessment_id"]
        user_id = data["user_id"]
        questions = data["questions"]

        print(f"\n✅ Assessment ID: {assessment_id}")
        print(f"✅ User ID: {user_id}")
        print(f"✅ Questions: {len(questions)}")
    else:
        print("❌ Failed to start assessment")
        return

    # ========================================================================
    # STEP 2: Check User Consents
    # ========================================================================
    print_header("Step 2: Check User Consents")

    response = requests.get(f"{API_URL}/api/v1/gdpr/consent/{user_id}")
    print_response(response)

    # ========================================================================
    # STEP 3: Get Privacy Info
    # ========================================================================
    print_header("Step 3: Get Privacy Information")

    response = requests.get(f"{API_URL}/api/v1/gdpr/privacy-info/{user_id}")
    print_response(response)

    if response.status_code == 200:
        privacy_info = response.json()
        print(f"\n📊 Data Summary:")
        print(f"  - Total Assessments: {privacy_info['data_summary']['total_assessments']}")
        print(f"  - Retention Days: {privacy_info['retention_info']['data_retention_days']}")
        print(f"  - Delete After: {privacy_info['retention_info']['delete_after']}")

    # ========================================================================
    # STEP 4: Answer Questions
    # ========================================================================
    print_header("Step 4: Submit Answers")

    # Simulate answers
    answers = []
    for i, q in enumerate(questions, 1):
        answer = (i % 4) + 2  # Varies between 2-5
        answers.append({
            "assessment_id": assessment_id,
            "question_id": q["question_id"],
            "answer": answer
        })

    print(f"📝 Submitting {len(answers)} answers...")

    submit_data = {
        "assessment_id": assessment_id,
        "answers": answers
    }

    response = requests.post(f"{API_URL}/api/v1/assessment/submit", json=submit_data)
    print_response(response)

    # ========================================================================
    # STEP 5: Get Audit Logs
    # ========================================================================
    print_header("Step 5: Check Audit Logs")

    response = requests.get(f"{API_URL}/api/v1/gdpr/audit/{user_id}?limit=10")
    print_response(response)

    if response.status_code == 200:
        logs = response.json()["logs"]
        print(f"\n📋 Recent Activities:")
        for log in logs:
            print(f"  - {log['action']} ({log['resource_type']}) at {log['timestamp']}")

    # ========================================================================
    # STEP 6: Export All User Data (GDPR: Right to Access)
    # ========================================================================
    print_header("Step 6: Export All User Data (Right to Access)")

    export_data = {
        "user_id": user_id,
        "email": email
    }

    response = requests.post(f"{API_URL}/api/v1/gdpr/export", json=export_data)
    print_response(response)

    if response.status_code == 200:
        export = response.json()
        print(f"\n📦 Export Summary:")
        print(f"  - User ID: {export['user_id']}")
        print(f"  - Export Date: {export['export_date']}")
        print(f"  - Data Keys: {list(export['data'].keys())}")

        # Save to file
        with open(f"user_data_export_{user_id}.json", "w") as f:
            json.dump(export, f, indent=2)
        print(f"\n💾 Data saved to: user_data_export_{user_id}.json")

    # ========================================================================
    # STEP 7: Withdraw Consent
    # ========================================================================
    print_header("Step 7: Withdraw Consent (Testing)")

    consent_data = {
        "user_id": user_id,
        "consent_type": "marketing",
        "consent_given": False,
        "purpose": "Marketing communications",
        "legal_basis": "consent"
    }

    response = requests.post(f"{API_URL}/api/v1/gdpr/consent", json=consent_data)
    print_response(response)

    # ========================================================================
    # STEP 8: Request Data Deletion (GDPR: Right to Erasure)
    # ========================================================================
    print_header("Step 8: Request Data Deletion (Right to be Forgotten)")

    delete_data = {
        "user_id": user_id,
        "email": email,
        "reason": "Testing GDPR deletion flow"
    }

    print("⚠️  Requesting deletion...")
    response = requests.post(f"{API_URL}/api/v1/gdpr/delete", json=delete_data)
    print_response(response)

    verification_token = None
    if response.status_code == 200:
        deletion_response = response.json()
        verification_token = deletion_response.get("verification_token")
        print(f"\n🔑 Verification Token: {verification_token}")

    # ========================================================================
    # STEP 9: Confirm Deletion
    # ========================================================================
    if verification_token:
        print_header("Step 9: Confirm Deletion")

        confirm = input("\n⚠️  Do you want to CONFIRM deletion? This will permanently delete all data. (yes/no): ")

        if confirm.lower() == "yes":
            response = requests.post(f"{API_URL}/api/v1/gdpr/delete/confirm/{verification_token}")
            print_response(response)

            if response.status_code == 200:
                print("\n✅ All user data has been permanently deleted")
        else:
            print("\n❌ Deletion cancelled")

    # ========================================================================
    # STEP 10: Get Privacy Policy
    # ========================================================================
    print_header("Step 10: Privacy Policy")

    response = requests.get(f"{API_URL}/api/v1/gdpr/privacy-policy")
    print_response(response)

    print_header("✅ GDPR TEST COMPLETE")


def test_admin_functions():
    """Test admin GDPR functions"""

    print_header("🔧 Admin GDPR Functions Test")

    admin_key = "CHANGE_ME_IN_PRODUCTION"

    # Test cleanup
    print("Testing data cleanup...")
    response = requests.post(f"{API_URL}/api/v1/gdpr/admin/cleanup?admin_key={admin_key}")
    print_response(response)

    # Test anonymization
    print("\nTesting data anonymization...")
    response = requests.post(
        f"{API_URL}/api/v1/gdpr/admin/anonymize?admin_key={admin_key}&days_threshold=90"
    )
    print_response(response)


def test_consent_without_required():
    """Test that assessment fails without required consents"""

    print_header("❌ Testing WITHOUT Required Consents (Should Fail)")

    start_data = {
        "email": "test2@example.com",
        "assessment_type": "disc",
        "language": "sv",
        "num_questions": 10,
        # MISSING REQUIRED CONSENTS
        "consent_data_processing": False,  # Should fail
        "consent_ai_analysis": True,
        "consent_storage": True
    }

    response = requests.post(f"{API_URL}/api/v1/assessment/start", json=start_data)

    if response.status_code == 403:
        print("✅ Correctly rejected - consent required!")
        print(f"   Error: {response.json()['detail']}")
    else:
        print("❌ FAILED - Should have rejected without consent")


def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║      🔒 GDPR-Compliant Assessment API - Test Suite            ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    print("\nChoose test mode:")
    print("1. Complete GDPR Flow Test (recommended)")
    print("2. Admin Functions Test")
    print("3. Consent Validation Test")
    print("4. All Tests")

    choice = input("\nYour choice (1-4): ").strip()

    try:
        if choice == "1":
            test_gdpr_complete_flow()
        elif choice == "2":
            test_admin_functions()
        elif choice == "3":
            test_consent_without_required()
        elif choice == "4":
            test_gdpr_complete_flow()
            test_admin_functions()
            test_consent_without_required()
        else:
            print("Invalid choice")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("Make sure the server is running on http://localhost:8000")
        print("\nStart server with: python api_main_gdpr.py")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
