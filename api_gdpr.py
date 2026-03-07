"""
GDPR-Extended API Endpoints
Additional endpoints for GDPR compliance
"""

from fastapi import APIRouter, Depends
from api_admin import verify_admin_token, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from database import (
    db, User, UserConsent, Assessment, AssessmentResult,
    AuditLog, DeletionRequest
)
import secrets

router = APIRouter(prefix="/api/v1/gdpr", tags=["GDPR"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ConsentRequest(BaseModel):
    """Request to give or withdraw consent"""
    user_id: str
    consent_type: str = Field(..., description="Type: data_processing, storage, ai_analysis, marketing")
    consent_given: bool
    purpose: str
    legal_basis: str = Field(default="consent", description="Legal basis: consent, legitimate_interest, contract")
    policy_version: str = Field(default="1.0")


class ConsentResponse(BaseModel):
    """Consent confirmation"""
    user_id: str
    consent_type: str
    consent_given: bool
    consent_date: datetime
    message: str


class DataExportRequest(BaseModel):
    """Request to export all user data"""
    user_id: str
    email: Optional[EmailStr] = None  # For verification


class DataExportResponse(BaseModel):
    """Complete user data export"""
    user_id: str
    export_date: datetime
    data: dict


class DeletionRequestModel(BaseModel):
    """Request to delete all user data"""
    user_id: str
    email: Optional[EmailStr] = None  # For verification
    reason: Optional[str] = None


class DeletionResponse(BaseModel):
    """Deletion confirmation"""
    user_id: str
    status: str
    verification_token: Optional[str] = None
    message: str


class PrivacyInfo(BaseModel):
    """Privacy information response"""
    user_id: str
    consents: List[dict]
    data_summary: dict
    retention_info: dict


# ============================================================================
# CONSENT MANAGEMENT
# ============================================================================

@router.post("/consent", response_model=ConsentResponse)
async def manage_consent(request: ConsentRequest, http_request: Request):
    """
    Give or withdraw consent for data processing

    GDPR Article 7: Conditions for consent
    - Freely given
    - Specific
    - Informed
    - Unambiguous
    """
    session = db.get_session()

    try:
        # Get or create user
        user = session.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if consent already exists
        existing_consent = session.query(UserConsent).filter(
            UserConsent.user_id == request.user_id,
            UserConsent.consent_type == request.consent_type
        ).first()

        if existing_consent:
            # Update existing consent
            if request.consent_given:
                existing_consent.consent_given = True
                existing_consent.consent_date = datetime.utcnow()
                existing_consent.consent_withdrawn_date = None
            else:
                # Withdraw consent
                existing_consent.consent_given = False
                existing_consent.consent_withdrawn_date = datetime.utcnow()

            consent = existing_consent
        else:
            # Create new consent
            consent = UserConsent(
                user_id=request.user_id,
                consent_type=request.consent_type,
                consent_given=request.consent_given,
                purpose=request.purpose,
                legal_basis=request.legal_basis,
                policy_version=request.policy_version
            )
            session.add(consent)

        # Audit log
        audit = AuditLog(
            user_id=request.user_id,
            action="consent_updated" if request.consent_given else "consent_withdrawn",
            resource_type="consent",
            resource_id=str(consent.id) if hasattr(consent, 'id') else None,
            details={
                "consent_type": request.consent_type,
                "consent_given": request.consent_given
            },
            ip_address=http_request.client.host if http_request.client else None
        )
        session.add(audit)

        session.commit()

        message = f"Consent {'given' if request.consent_given else 'withdrawn'} successfully"

        return ConsentResponse(
            user_id=request.user_id,
            consent_type=request.consent_type,
            consent_given=request.consent_given,
            consent_date=consent.consent_date,
            message=message
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/consent/{user_id}")
async def get_user_consents(user_id: str):
    """
    Get all consents for a user

    GDPR: Transparency - users should know what they've consented to
    """
    session = db.get_session()

    try:
        consents = session.query(UserConsent).filter(
            UserConsent.user_id == user_id
        ).all()

        return {
            "user_id": user_id,
            "consents": [c.to_dict() for c in consents]
        }

    finally:
        session.close()


# ============================================================================
# DATA ACCESS (Right to Access - GDPR Article 15)
# ============================================================================

@router.post("/export", response_model=DataExportResponse)
async def export_user_data(
    request: DataExportRequest,
    session: dict = Depends(verify_admin_token)  # SECURITY: Require admin auth
):
    """Export user data - ADMIN ONLY for security"""request: DataExportRequest):
    """
    Export all user data in portable format

    GDPR Article 15: Right of access by the data subject
    GDPR Article 20: Right to data portability
    """
    session = db.get_session()

    try:
        # Get user
        user = session.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify email if provided
        if request.email:
            import hashlib
            email_hash = hashlib.sha256(request.email.encode()).hexdigest()
            if user.email_hash != email_hash:
                raise HTTPException(status_code=403, detail="Email verification failed")

        # Export all data
        user_data = user.to_dict()

        # Audit log
        audit = AuditLog(
            user_id=request.user_id,
            action="data_exported",
            resource_type="user",
            resource_id=request.user_id,
            details={"export_type": "full"}
        )
        session.add(audit)
        session.commit()

        return DataExportResponse(
            user_id=request.user_id,
            export_date=datetime.utcnow(),
            data=user_data
        )

    finally:
        session.close()


@router.get("/privacy-info/{user_id}", response_model=PrivacyInfo)
async def get_privacy_info(user_id: str):
    """
    Get privacy information for a user

    Shows what data is stored and for how long
    """
    session = db.get_session()

    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get consents
        consents = session.query(UserConsent).filter(
            UserConsent.user_id == user_id
        ).all()

        # Get assessments count
        assessments = session.query(Assessment).filter(
            Assessment.user_id == user_id
        ).all()

        data_summary = {
            "total_assessments": len(assessments),
            "completed_assessments": len([a for a in assessments if a.status == "completed"]),
            "anonymized_assessments": len([a for a in assessments if a.is_anonymized])
        }

        retention_info = {
            "data_retention_days": user.data_retention_days,
            "delete_after": user.delete_after.isoformat() if user.delete_after else None,
            "days_until_deletion": (user.delete_after - datetime.utcnow()).days if user.delete_after else None
        }

        return PrivacyInfo(
            user_id=user_id,
            consents=[c.to_dict() for c in consents],
            data_summary=data_summary,
            retention_info=retention_info
        )

    finally:
        session.close()


# ============================================================================
# DATA DELETION (Right to Erasure - GDPR Article 17)
# ============================================================================

@router.post("/delete", response_model=DeletionResponse)
async def request_data_deletion(request: DeletionRequestModel):
    """
    Request deletion of all user data

    GDPR Article 17: Right to erasure ('right to be forgotten')

    This creates a deletion request that can be verified and processed
    """
    session = db.get_session()

    try:
        # Get user
        user = session.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify email if provided
        if request.email:
            import hashlib
            email_hash = hashlib.sha256(request.email.encode()).hexdigest()
            if user.email_hash != email_hash:
                raise HTTPException(status_code=403, detail="Email verification failed")

        # Create deletion request
        deletion_req = DeletionRequest(
            user_id=request.user_id,
            reason=request.reason
        )
        session.add(deletion_req)

        # Audit log
        audit = AuditLog(
            user_id=request.user_id,
            action="deletion_requested",
            resource_type="user",
            resource_id=request.user_id,
            details={"reason": request.reason}
        )
        session.add(audit)

        session.commit()

        return DeletionResponse(
            user_id=request.user_id,
            status="pending",
            verification_token=deletion_req.verification_token,
            message=f"Deletion request created. Use verification token to confirm deletion."
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.post("/delete/confirm/{verification_token}")
async def confirm_deletion(verification_token: str):
    """
    Confirm and execute data deletion

    Requires verification token from deletion request
    """
    session = db.get_session()

    try:
        # Find deletion request
        deletion_req = session.query(DeletionRequest).filter(
            DeletionRequest.verification_token == verification_token,
            DeletionRequest.status == "pending"
        ).first()

        if not deletion_req:
            raise HTTPException(status_code=404, detail="Deletion request not found or already processed")

        user_id = deletion_req.user_id

        # Get user
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Mark deletion request as processing
        deletion_req.status = "processing"
        deletion_req.verified_at = datetime.utcnow()
        session.commit()

        # Final audit log before deletion
        audit = AuditLog(
            user_id=user_id,
            action="user_deleted",
            resource_type="user",
            resource_id=user_id,
            details={
                "reason": deletion_req.reason,
                "assessments_deleted": len(user.assessments)
            }
        )
        session.add(audit)
        session.commit()

        # Delete user (cascade deletes all related data)
        session.delete(user)

        # Mark deletion request as completed
        deletion_req.status = "completed"
        deletion_req.processed_at = datetime.utcnow()

        session.commit()

        return {
            "status": "completed",
            "message": f"All data for user {user_id} has been permanently deleted",
            "deleted_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        session.rollback()
        if deletion_req:
            deletion_req.status = "failed"
            session.commit()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/delete/immediate/{user_id}")
async def delete_user_immediately(user_id: str, confirmation: str):
    """
    Immediately delete user data (admin/emergency use)

    WARNING: This permanently deletes all user data without verification
    Requires confirmation string to prevent accidental deletion
    """
    if confirmation != f"DELETE_{user_id}":
        raise HTTPException(
            status_code=400,
            detail=f"Confirmation failed. Must provide: DELETE_{user_id}"
        )

    session = db.get_session()

    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="user_deleted_immediate",
            resource_type="user",
            resource_id=user_id,
            details={"method": "immediate_deletion"}
        )
        session.add(audit)
        session.commit()

        # Delete
        session.delete(user)
        session.commit()

        return {
            "status": "deleted",
            "message": f"User {user_id} and all associated data permanently deleted",
            "deleted_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# ============================================================================
# DATA RECTIFICATION (GDPR Article 16)
# ============================================================================

@router.put("/rectify/{user_id}")
async def rectify_user_data(user_id: str, data_retention_days: Optional[int] = None):
    """
    Update/rectify user data

    GDPR Article 16: Right to rectification

    Currently supports updating data retention period
    """
    session = db.get_session()

    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        changes = {}

        if data_retention_days is not None:
            user.data_retention_days = data_retention_days
            from datetime import timedelta
            user.delete_after = datetime.utcnow() + timedelta(days=data_retention_days)
            changes["data_retention_days"] = data_retention_days

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="data_rectified",
            resource_type="user",
            resource_id=user_id,
            details={"changes": changes}
        )
        session.add(audit)

        session.commit()

        return {
            "status": "updated",
            "user_id": user_id,
            "changes": changes,
            "message": "User data updated successfully"
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# ============================================================================
# AUDIT LOGS (GDPR Article 30: Records of processing activities)
# ============================================================================

@router.get("/audit/{user_id}")
async def get_audit_logs(user_id: str, limit: int = 100):
    """
    Get audit logs for a user

    GDPR Article 30: Records of processing activities
    Shows all data processing activities for transparency
    """
    session = db.get_session()

    try:
        logs = session.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()

        return {
            "user_id": user_id,
            "total_logs": len(logs),
            "logs": [log.to_dict() for log in logs]
        }

    finally:
        session.close()


# ============================================================================
# ADMIN ENDPOINTS (Data Protection Officer use)
# ============================================================================

@router.post("/admin/cleanup")
async def cleanup_expired_data(admin_key: str):
    """
    Clean up expired data (run periodically)

    GDPR: Data retention - automatically delete data past retention period
    Requires admin key for security
    """
    # In production, verify admin_key against environment variable
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Admin API not configured")

    if not secrets.compare_digest(admin_key, ADMIN_API_KEY):
        raise HTTPException(status_code=403, detail="Invalid admin key")

    try:
        deleted_count = db.cleanup_expired_data()

        return {
            "status": "completed",
            "users_deleted": deleted_count,
            "message": f"Cleaned up {deleted_count} expired user accounts"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/anonymize")
async def anonymize_old_data(admin_key: str, days_threshold: int = 90):
    """
    Anonymize old assessments

    GDPR: Data minimization - remove personal identifiers from old data
    while keeping statistical value
    """
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Admin API not configured")

    if not secrets.compare_digest(admin_key, ADMIN_API_KEY):
        raise HTTPException(status_code=403, detail="Invalid admin key")

    try:
        anonymized_count = db.anonymize_old_assessments(days_threshold)

        return {
            "status": "completed",
            "assessments_anonymized": anonymized_count,
            "days_threshold": days_threshold,
            "message": f"Anonymized {anonymized_count} assessments older than {days_threshold} days"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRIVACY POLICY & COMPLIANCE INFO
# ============================================================================

@router.get("/privacy-policy")
async def get_privacy_policy():
    """
    Return privacy policy information

    GDPR Article 13: Information to be provided
    """
    return {
        "policy_version": "1.0",
        "last_updated": "2024-01-01",
        "data_controller": {
            "name": "Your Company Name",
            "email": "privacy@yourcompany.com",
            "address": "Your Address"
        },
        "data_collected": [
            {
                "type": "Assessment responses",
                "purpose": "Personality assessment and analysis",
                "legal_basis": "Consent",
                "retention": "Up to 365 days or until deletion requested"
            },
            {
                "type": "Usage data",
                "purpose": "Service improvement and analytics",
                "legal_basis": "Legitimate interest",
                "retention": "90 days (anonymized after)"
            }
        ],
        "your_rights": [
            "Right to access your data (Article 15)",
            "Right to rectification (Article 16)",
            "Right to erasure (Article 17)",
            "Right to data portability (Article 20)",
            "Right to withdraw consent (Article 7)",
            "Right to lodge a complaint with supervisory authority"
        ],
        "data_processing": {
            "ai_analysis": "We use Anthropic Claude AI to analyze your assessment responses",
            "third_parties": ["Anthropic (AI processing)"],
            "data_transfer": "Data may be processed in US (Anthropic servers)",
            "security_measures": "Encryption, pseudonymization, access controls"
        },
        "contact": {
            "dpo_email": "dpo@yourcompany.com",
            "support_email": "support@yourcompany.com"
        }
    }
