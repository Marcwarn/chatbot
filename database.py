"""
GDPR-Compliant Database Models
SQLAlchemy models för personality assessment med full GDPR support
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import json
import enum

Base = declarative_base()

# ============================================================================
# ENUMS
# ============================================================================

class AssessmentType(enum.Enum):
    """Assessment type enumeration"""
    BIG_FIVE = "big_five"
    DISC = "disc"

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
    Supports both Big Five and DISC assessments
    """
    __tablename__ = "assessments"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    assessment_type = Column(Enum(AssessmentType), nullable=False, default=AssessmentType.BIG_FIVE)
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
            "assessment_type": self.assessment_type.value if isinstance(self.assessment_type, AssessmentType) else self.assessment_type,
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
    Supports both Big Five and DISC results
    """
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String, ForeignKey("assessments.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Results stored as JSON for flexibility (works for both Big Five and DISC)
    scores = Column(JSON, nullable=False)  # List of dimension scores
    summary = Column(Text, nullable=False)
    detailed_analysis = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=False)  # List of strengths
    development_areas = Column(JSON, nullable=False)  # List of areas
    recommendations = Column(JSON, nullable=False)  # List of recommendations

    # DISC-specific fields (nullable for backward compatibility with Big Five)
    dominance_score = Column(Float, nullable=True)
    influence_score = Column(Float, nullable=True)
    steadiness_score = Column(Float, nullable=True)
    conscientiousness_score = Column(Float, nullable=True)
    disc_profile = Column(String, nullable=True)  # e.g., "Di", "SC", "D"

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
# SECURITY EVENT MODELS
# ============================================================================

class SecurityEvent(Base):
    """
    Track security events for monitoring and analytics
    """
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Event details
    event_type = Column(String, nullable=False)  # brute_force, sql_injection, etc.
    severity = Column(String, nullable=False)     # low, medium, high, critical
    client_ip = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)

    # User context (if authenticated)
    user_id = Column(String, nullable=True)

    # Additional details
    user_agent = Column(String, nullable=True)
    details = Column(JSON, nullable=True)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Response
    was_blocked = Column(Boolean, default=False)
    block_duration = Column(Integer, nullable=True)  # seconds

    def to_dict(self):
        """Export event data"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "severity": self.severity,
            "client_ip": self.client_ip,
            "endpoint": self.endpoint,
            "user_id": self.user_id,
            "user_agent": self.user_agent,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "was_blocked": self.was_blocked,
            "block_duration": self.block_duration
        }


class BlockedIP(Base):
    """
    Track blocked IPs
    """
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, autoincrement=True)

    ip_address = Column(String, nullable=False, unique=True, index=True)
    reason = Column(String, nullable=False)
    block_count = Column(Integer, default=1)  # Number of times blocked

    # Timestamps
    first_blocked_at = Column(DateTime, default=datetime.utcnow)
    last_blocked_at = Column(DateTime, default=datetime.utcnow)
    unblock_at = Column(DateTime, nullable=False, index=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_permanent = Column(Boolean, default=False)

    def to_dict(self):
        """Export blocked IP data"""
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "reason": self.reason,
            "block_count": self.block_count,
            "first_blocked_at": self.first_blocked_at.isoformat(),
            "last_blocked_at": self.last_blocked_at.isoformat(),
            "unblock_at": self.unblock_at.isoformat() if self.unblock_at else None,
            "is_active": self.is_active,
            "is_permanent": self.is_permanent
        }


class SecurityMetric(Base):
    """
    Store aggregated security metrics for analytics
    """
    __tablename__ = "security_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)

    metric_type = Column(String, nullable=False)  # failed_logins, rate_violations, etc.
    metric_value = Column(Integer, nullable=False)
    time_bucket = Column(DateTime, nullable=False, index=True)  # Hourly buckets

    # Additional context
    metric_metadata = Column(JSON, nullable=True)

    def to_dict(self):
        """Export metric data"""
        return {
            "metric_type": self.metric_type,
            "metric_value": self.metric_value,
            "time_bucket": self.time_bucket.isoformat(),
            "metadata": self.metric_metadata
        }


class IncidentReport(Base):
    """
    Store incident reports for major security events
    """
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)

    incident_id = Column(String, unique=True, nullable=False)
    incident_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)

    # Incident details
    client_ip = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    full_report = Column(Text, nullable=True)

    # Event references
    related_events = Column(JSON, nullable=True)  # List of event IDs

    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Status
    status = Column(String, default="open")  # open, investigating, resolved, false_positive

    # Actions taken
    actions_taken = Column(JSON, nullable=True)

    def to_dict(self):
        """Export incident data"""
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "incident_type": self.incident_type,
            "severity": self.severity,
            "client_ip": self.client_ip,
            "endpoint": self.endpoint,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "status": self.status,
            "actions_taken": self.actions_taken
        }


# ============================================================================
# COST TRACKING MODELS
# ============================================================================

class APIUsage(Base):
    """
    Track API usage for cost analysis
    Records all API calls with token counts and costs
    """
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Service details
    service = Column(String, nullable=False, index=True)  # "anthropic", "database", "hosting"
    feature = Column(String, nullable=False, index=True)  # "report_generation", "chat", etc.

    # Anthropic-specific fields
    model = Column(String, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    cost = Column(Float, nullable=False)

    # Context
    user_id = Column(String, nullable=True, index=True)
    assessment_id = Column(String, nullable=True, index=True)

    # Optimization tracking
    cache_hit = Column(Boolean, default=False)
    execution_time_ms = Column(Float, nullable=True)

    # Additional metadata
    metadata = Column(JSON, nullable=True)

    def to_dict(self):
        """Export usage data"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "service": self.service,
            "feature": self.feature,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "user_id": self.user_id,
            "assessment_id": self.assessment_id,
            "cache_hit": self.cache_hit,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata
        }


class CostBudget(Base):
    """
    Store budget settings and alerts
    """
    __tablename__ = "cost_budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Budget configuration
    period = Column(String, nullable=False)  # "monthly", "daily", "weekly"
    budget_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")

    # Alert settings
    alert_thresholds = Column(JSON, nullable=False)  # [50, 80, 100] percentages
    alert_enabled = Column(Boolean, default=True)
    alert_email = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        """Export budget configuration"""
        return {
            "id": self.id,
            "period": self.period,
            "budget_amount": self.budget_amount,
            "currency": self.currency,
            "alert_thresholds": self.alert_thresholds,
            "alert_enabled": self.alert_enabled,
            "alert_email": self.alert_email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "effective_from": self.effective_from.isoformat(),
            "effective_to": self.effective_to.isoformat() if self.effective_to else None,
            "is_active": self.is_active
        }


class CostAlert(Base):
    """
    Store cost alert history
    """
    __tablename__ = "cost_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Alert details
    alert_level = Column(String, nullable=False)  # "green", "yellow", "orange", "red"
    threshold_percentage = Column(Float, nullable=False)
    current_spend = Column(Float, nullable=False)
    budget_amount = Column(Float, nullable=False)
    projected_spend = Column(Float, nullable=True)

    # Message
    message = Column(Text, nullable=False)
    requires_action = Column(Boolean, default=False)

    # Timestamps
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Status
    status = Column(String, default="active")  # active, acknowledged, resolved

    def to_dict(self):
        """Export alert data"""
        return {
            "id": self.id,
            "alert_level": self.alert_level,
            "threshold_percentage": self.threshold_percentage,
            "current_spend": self.current_spend,
            "budget_amount": self.budget_amount,
            "projected_spend": self.projected_spend,
            "message": self.message,
            "requires_action": self.requires_action,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "status": self.status
        }


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

    # ── Security Event Methods ──────────────────────────────────────────────

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        client_ip: str,
        endpoint: str,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
        was_blocked: bool = False,
        block_duration: Optional[int] = None
    ):
        """Log a security event to database"""
        session = self.get_session()

        try:
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                client_ip=client_ip,
                endpoint=endpoint,
                user_id=user_id,
                user_agent=user_agent,
                details=details,
                was_blocked=was_blocked,
                block_duration=block_duration
            )

            session.add(event)
            session.commit()

            return event.id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_security_events(
        self,
        hours: int = 24,
        event_type: Optional[str] = None,
        client_ip: Optional[str] = None,
        limit: int = 100
    ):
        """Get recent security events"""
        session = self.get_session()

        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)

            query = session.query(SecurityEvent).filter(
                SecurityEvent.timestamp >= cutoff
            )

            if event_type:
                query = query.filter(SecurityEvent.event_type == event_type)

            if client_ip:
                query = query.filter(SecurityEvent.client_ip == client_ip)

            events = query.order_by(SecurityEvent.timestamp.desc()).limit(limit).all()

            return [e.to_dict() for e in events]

        finally:
            session.close()

    def block_ip(
        self,
        ip_address: str,
        reason: str,
        duration_seconds: int,
        is_permanent: bool = False
    ):
        """Block an IP address"""
        session = self.get_session()

        try:
            # Check if IP already blocked
            blocked = session.query(BlockedIP).filter(
                BlockedIP.ip_address == ip_address,
                BlockedIP.is_active == True
            ).first()

            if blocked:
                # Update existing block
                blocked.block_count += 1
                blocked.last_blocked_at = datetime.utcnow()
                blocked.unblock_at = datetime.utcnow() + timedelta(seconds=duration_seconds)
                blocked.is_permanent = is_permanent
                blocked.reason = reason
            else:
                # Create new block
                blocked = BlockedIP(
                    ip_address=ip_address,
                    reason=reason,
                    unblock_at=datetime.utcnow() + timedelta(seconds=duration_seconds) if not is_permanent else None,
                    is_permanent=is_permanent
                )
                session.add(blocked)

            session.commit()

            return blocked.id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_blocked_ips(self, include_expired: bool = False):
        """Get list of blocked IPs"""
        session = self.get_session()

        try:
            query = session.query(BlockedIP).filter(
                BlockedIP.is_active == True
            )

            if not include_expired:
                now = datetime.utcnow()
                query = query.filter(
                    (BlockedIP.is_permanent == True) |
                    (BlockedIP.unblock_at > now)
                )

            blocked_ips = query.all()

            return [ip.to_dict() for ip in blocked_ips]

        finally:
            session.close()

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is currently blocked"""
        session = self.get_session()

        try:
            now = datetime.utcnow()

            blocked = session.query(BlockedIP).filter(
                BlockedIP.ip_address == ip_address,
                BlockedIP.is_active == True,
                (BlockedIP.is_permanent == True) |
                (BlockedIP.unblock_at > now)
            ).first()

            return blocked is not None

        finally:
            session.close()

    def cleanup_expired_blocks(self):
        """Remove expired IP blocks"""
        session = self.get_session()

        try:
            now = datetime.utcnow()

            expired = session.query(BlockedIP).filter(
                BlockedIP.is_active == True,
                BlockedIP.is_permanent == False,
                BlockedIP.unblock_at <= now
            ).all()

            for block in expired:
                block.is_active = False

            session.commit()

            return len(expired)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_incident_report(
        self,
        incident_id: str,
        incident_type: str,
        severity: str,
        client_ip: str,
        endpoint: str,
        description: str,
        full_report: Optional[str] = None,
        related_events: Optional[list] = None,
        actions_taken: Optional[dict] = None
    ):
        """Create an incident report"""
        session = self.get_session()

        try:
            report = IncidentReport(
                incident_id=incident_id,
                incident_type=incident_type,
                severity=severity,
                client_ip=client_ip,
                endpoint=endpoint,
                description=description,
                full_report=full_report,
                related_events=related_events,
                actions_taken=actions_taken
            )

            session.add(report)
            session.commit()

            return report.id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# Initialize database with environment variable support
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./assessment_gdpr.db")

# Vercel Postgres URLs use 'postgres://' but SQLAlchemy needs 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

db = Database(DATABASE_URL)

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
