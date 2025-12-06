"""
GDPR-Compliant Database Models
SQLAlchemy models för personality assessment med full GDPR support
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import json

Base = declarative_base()

# ============================================================================
# USER & CONSENT MODELS
# ============================================================================

class User(Base):
    """
    User model - minimal data (GDPR: Data Minimization)
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Pseudonymous ID
    email_hash = Column(String, unique=True, nullable=True)  # Hashed email (not plaintext)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # GDPR: Data retention
    data_retention_days = Column(Integer, default=365)  # Auto-delete after 1 year
    delete_after = Column(DateTime, nullable=True)

    # Relationships
    consents = relationship("UserConsent", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email: Optional[str] = None, user_id: Optional[str] = None):
        """Create user with pseudonymous ID"""
        if user_id:
            self.id = user_id
        else:
            self.id = f"user_{secrets.token_urlsafe(16)}"

        if email:
            self.email_hash = hashlib.sha256(email.encode()).hexdigest()

        # Set auto-delete date
        self.delete_after = datetime.utcnow() + timedelta(days=self.data_retention_days)

    def to_dict(self):
        """Export user data (GDPR: Right to Access)"""
        return {
            "user_id": self.id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "data_retention_days": self.data_retention_days,
            "delete_after": self.delete_after.isoformat() if self.delete_after else None,
            "consents": [c.to_dict() for c in self.consents],
            "assessments": [a.to_dict() for a in self.assessments]
        }


class UserConsent(Base):
    """
    GDPR Consent Management
    Tracks what user has consented to and when
    """
    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Consent types
    consent_type = Column(String, nullable=False)  # e.g., "data_processing", "storage", "ai_analysis"
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime, default=datetime.utcnow)
    consent_withdrawn_date = Column(DateTime, nullable=True)

    # Consent details
    purpose = Column(Text, nullable=False)  # What the data will be used for
    legal_basis = Column(String, nullable=False)  # e.g., "consent", "legitimate_interest"

    # Version tracking (if privacy policy changes)
    policy_version = Column(String, default="1.0")

    user = relationship("User", back_populates="consents")

    def to_dict(self):
        return {
            "consent_type": self.consent_type,
            "consent_given": self.consent_given,
            "consent_date": self.consent_date.isoformat(),
            "consent_withdrawn": self.consent_withdrawn_date.isoformat() if self.consent_withdrawn_date else None,
            "purpose": self.purpose,
            "legal_basis": self.legal_basis,
            "policy_version": self.policy_version
        }


# ============================================================================
# ASSESSMENT MODELS
# ============================================================================

class Assessment(Base):
    """
    Assessment model with GDPR compliance
    """
    __tablename__ = "assessments"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    assessment_type = Column(String, nullable=False)
    language = Column(String, default="sv")
    status = Column(String, default="in_progress")  # in_progress, completed, deleted

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # GDPR: Anonymized storage
    # Questions and answers stored separately, can be anonymized
    is_anonymized = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    answers = relationship("AssessmentAnswer", back_populates="assessment", cascade="all, delete-orphan")
    result = relationship("AssessmentResult", back_populates="assessment", uselist=False, cascade="all, delete-orphan")

    def to_dict(self, include_questions=True, include_answers=True, include_result=True):
        """Export assessment data (GDPR: Right to Access)"""
        data = {
            "assessment_id": self.id,
            "assessment_type": self.assessment_type,
            "language": self.language,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_anonymized": self.is_anonymized
        }

        if include_questions:
            data["questions"] = [q.to_dict() for q in self.questions]

        if include_answers:
            data["answers"] = [a.to_dict() for a in self.answers]

        if include_result and self.result:
            data["result"] = self.result.to_dict()

        return data

    def anonymize(self):
        """
        Anonymize assessment data (GDPR: Data Protection)
        Removes link to user while keeping statistical data
        """
        self.user_id = "anonymous"
        self.is_anonymized = True

        # Remove any PII from answers (if any free text)
        for answer in self.answers:
            if isinstance(answer.answer_value, str) and len(answer.answer_value) > 100:
                answer.answer_value = "[REDACTED - Free text answer]"


class AssessmentQuestion(Base):
    """
    Questions for an assessment
    """
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)

    question_id = Column(Integer, nullable=False)  # Question number
    question_text = Column(Text, nullable=False)
    scale_type = Column(String, nullable=False)  # likert, choice, open
    options = Column(JSON, nullable=True)  # Stored as JSON
    dimension = Column(String, nullable=False)

    assessment = relationship("Assessment", back_populates="questions")

    def to_dict(self):
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "scale_type": self.scale_type,
            "options": self.options,
            "dimension": self.dimension
        }


class AssessmentAnswer(Base):
    """
    User answers to assessment questions
    """
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, nullable=False)

    answer_value = Column(String, nullable=False)  # Store as string, convert as needed
    answered_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="answers")

    def to_dict(self):
        return {
            "question_id": self.question_id,
            "answer": self.answer_value,
            "answered_at": self.answered_at.isoformat()
        }


class AssessmentResult(Base):
    """
    Assessment results and analysis
    """
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String, ForeignKey("assessments.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Results stored as JSON for flexibility
    scores = Column(JSON, nullable=False)  # List of dimension scores
    summary = Column(Text, nullable=False)
    detailed_analysis = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=False)  # List of strengths
    development_areas = Column(JSON, nullable=False)  # List of areas
    recommendations = Column(JSON, nullable=False)  # List of recommendations

    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="result")

    def to_dict(self):
        return {
            "assessment_id": self.assessment_id,
            "scores": self.scores,
            "summary": self.summary,
            "detailed_analysis": self.detailed_analysis,
            "strengths": self.strengths,
            "development_areas": self.development_areas,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }


# ============================================================================
# AUDIT LOG (GDPR: Accountability)
# ============================================================================

class AuditLog(Base):
    """
    Audit log for all data processing activities (GDPR: Accountability)
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    action = Column(String, nullable=False)  # e.g., "data_created", "data_accessed", "data_deleted"
    resource_type = Column(String, nullable=False)  # e.g., "assessment", "user", "consent"
    resource_id = Column(String, nullable=True)

    details = Column(JSON, nullable=True)  # Additional context
    ip_address = Column(String, nullable=True)  # For security tracking

    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

    def to_dict(self):
        return {
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


# ============================================================================
# DATA DELETION REQUESTS (GDPR: Right to Erasure)
# ============================================================================

class DeletionRequest(Base):
    """
    Track deletion requests (Right to be Forgotten)
    """
    __tablename__ = "deletion_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)  # No FK - user might be deleted

    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed

    # Reason (optional)
    reason = Column(Text, nullable=True)

    # Verification
    verification_token = Column(String, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    def __init__(self, user_id: str, reason: Optional[str] = None):
        self.user_id = user_id
        self.reason = reason
        self.verification_token = secrets.token_urlsafe(32)


# ============================================================================
# DATABASE SETUP
# ============================================================================

class Database:
    """Database manager with GDPR utilities"""

    def __init__(self, database_url: str = "sqlite:///./assessment_gdpr.db"):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def cleanup_expired_data(self):
        """
        Auto-delete expired data (GDPR: Data Retention)
        Should be run periodically (e.g., daily cron job)
        """
        session = self.get_session()

        try:
            # Find users past their retention period
            expired_users = session.query(User).filter(
                User.delete_after <= datetime.utcnow(),
                User.is_active == True
            ).all()

            for user in expired_users:
                # Log deletion
                audit = AuditLog(
                    user_id=user.id,
                    action="auto_delete_expired",
                    resource_type="user",
                    resource_id=user.id,
                    details={"reason": "data_retention_expired"}
                )
                session.add(audit)

                # Delete user (cascade deletes all related data)
                session.delete(user)

            session.commit()
            return len(expired_users)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def anonymize_old_assessments(self, days_threshold: int = 90):
        """
        Anonymize assessments older than threshold
        Keeps statistical data but removes user link
        """
        session = self.get_session()

        try:
            threshold_date = datetime.utcnow() - timedelta(days=days_threshold)

            old_assessments = session.query(Assessment).filter(
                Assessment.completed_at <= threshold_date,
                Assessment.is_anonymized == False,
                Assessment.status == "completed"
            ).all()

            for assessment in old_assessments:
                assessment.anonymize()

                # Log anonymization
                audit = AuditLog(
                    user_id=assessment.user_id,
                    action="data_anonymized",
                    resource_type="assessment",
                    resource_id=assessment.id,
                    details={"threshold_days": days_threshold}
                )
                session.add(audit)

            session.commit()
            return len(old_assessments)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# Initialize database
db = Database()

if __name__ == "__main__":
    # Create tables
    db.create_tables()
    print("✅ GDPR-compliant database tables created!")

    # Test user creation
    session = db.get_session()

    test_user = User(email="test@example.com")
    session.add(test_user)

    # Add consent
    consent = UserConsent(
        user_id=test_user.id,
        consent_type="data_processing",
        consent_given=True,
        purpose="Personality assessment and analysis",
        legal_basis="consent"
    )
    session.add(consent)

    # Add audit log
    audit = AuditLog(
        user_id=test_user.id,
        action="user_created",
        resource_type="user",
        resource_id=test_user.id
    )
    session.add(audit)

    session.commit()

    print(f"✅ Test user created: {test_user.id}")
    print(f"✅ Email hash: {test_user.email_hash[:16]}...")
    print(f"✅ Auto-delete date: {test_user.delete_after}")

    session.close()
