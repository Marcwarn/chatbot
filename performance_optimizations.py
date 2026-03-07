"""
Performance Optimizations for Personality Assessment API
Addresses N+1 queries, caching, connection pooling, and async operations
"""

from sqlalchemy import Index, create_engine
from sqlalchemy.orm import sessionmaker, joinedload, selectinload
from sqlalchemy.pool import QueuePool
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json
import os

# ============================================================================
# DATABASE CONNECTION POOLING
# ============================================================================

def create_optimized_engine(database_url: str):
    """
    Create SQLAlchemy engine with optimized connection pooling

    Performance improvements:
    - Connection pooling prevents overhead of creating new connections
    - Pool recycling prevents stale connections
    - Proper pool sizing for concurrent requests
    """
    return create_engine(
        database_url,
        echo=False,

        # Connection pooling configuration
        poolclass=QueuePool,
        pool_size=20,              # Base pool size (handles ~20 concurrent requests)
        max_overflow=40,           # Additional connections under load (total 60)
        pool_timeout=30,           # Wait time for connection from pool
        pool_recycle=3600,         # Recycle connections every hour (prevents stale connections)
        pool_pre_ping=True,        # Verify connection health before using

        # Query optimization
        connect_args={
            "options": "-c timezone=utc",
            "connect_timeout": 10,
        } if "postgresql" in database_url else {},

        # Performance settings
        execution_options={
            "compiled_cache_size": 500,  # Cache compiled SQL statements
        }
    )


# ============================================================================
# DATABASE INDEX CREATION
# ============================================================================

def create_performance_indexes(engine):
    """
    Create database indexes to optimize query performance

    Indexes dramatically speed up WHERE, JOIN, and ORDER BY operations.
    Without indexes, queries do full table scans (slow for large datasets).

    Performance impact: 10-100x faster queries on indexed columns
    """
    from database import Base, User, Assessment, AssessmentAnswer, AuditLog, DeletionRequest, UserConsent

    # Create indexes using raw SQL for maximum compatibility
    with engine.connect() as conn:
        # User indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email_hash
            ON users(email_hash)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_delete_after
            ON users(delete_after)
            WHERE delete_after IS NOT NULL
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_active
            ON users(is_active, last_active)
        """)

        # Assessment indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessments_user_id
            ON assessments(user_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessments_status
            ON assessments(status, completed_at)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessments_completed_at
            ON assessments(completed_at)
            WHERE completed_at IS NOT NULL
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_assessments_anonymized
            ON assessments(is_anonymized, completed_at)
        """)

        # Assessment answers index (for JOIN performance)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_answers_assessment_id
            ON assessment_answers(assessment_id)
        """)

        # Audit log indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_user_timestamp
            ON audit_logs(user_id, timestamp DESC)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_action_timestamp
            ON audit_logs(action, timestamp DESC)
        """)

        # User consent index
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_consent_user_type
            ON user_consents(user_id, consent_type)
        """)

        # Deletion requests index
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_deletion_token
            ON deletion_requests(verification_token)
            WHERE status = 'pending'
        """)

        conn.commit()

    print("✅ Performance indexes created successfully")


# ============================================================================
# OPTIMIZED DATABASE QUERIES (Fixes N+1 Problems)
# ============================================================================

class OptimizedQueries:
    """
    Optimized database queries that fix N+1 problems using eager loading

    N+1 Problem Example:
    - BAD: Query 1 user, then loop through assessments querying each one (1 + N queries)
    - GOOD: Query 1 user WITH all assessments in single query (1 query total)
    """

    def __init__(self, session):
        self.session = session

    def get_user_with_all_data(self, user_id: str):
        """
        Get user with ALL related data in ONE query (fixes N+1)

        Performance: 1 query instead of 5+ queries
        """
        from database import User

        return self.session.query(User).options(
            joinedload(User.consents),           # Eager load consents
            joinedload(User.assessments).joinedload('questions'),  # Eager load assessments + questions
            joinedload(User.assessments).joinedload('answers'),    # Eager load answers
            joinedload(User.assessments).joinedload('result'),     # Eager load results
        ).filter(User.id == user_id).first()

    def get_users_batch(self, user_ids: List[str]):
        """
        Get multiple users in single query (batch processing)

        Performance: 1 query for 100 users vs 100 queries
        """
        from database import User

        return self.session.query(User).filter(
            User.id.in_(user_ids)
        ).all()

    def get_recent_assessments_optimized(self, days: int = 7, limit: int = 100):
        """
        Get recent assessments with eager loading (fixes N+1)
        """
        from database import Assessment

        cutoff = datetime.utcnow() - timedelta(days=days)

        return self.session.query(Assessment).options(
            joinedload(Assessment.user),
            joinedload(Assessment.result),
        ).filter(
            Assessment.completed_at >= cutoff
        ).order_by(
            Assessment.completed_at.desc()
        ).limit(limit).all()

    def get_expiring_users_batch(self, batch_size: int = 100):
        """
        Get expiring users in batches for efficient cleanup
        """
        from database import User

        return self.session.query(User).filter(
            User.delete_after <= datetime.utcnow(),
            User.is_active == True
        ).limit(batch_size).all()

    def get_user_audit_logs_optimized(self, user_id: str, limit: int = 100):
        """
        Get audit logs efficiently with proper indexing usage
        """
        from database import AuditLog

        # Uses idx_audit_user_timestamp index
        return self.session.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).all()


# ============================================================================
# LAZY LOADING STRATEGY
# ============================================================================

class LazyDataLoader:
    """
    Implement lazy loading for expensive operations
    Load data only when needed, not all at once
    """

    def __init__(self, session):
        self.session = session
        self._cache = {}

    def get_assessment_result(self, assessment_id: str):
        """
        Lazy load assessment result only when accessed
        """
        if assessment_id in self._cache:
            return self._cache[assessment_id]

        from database import AssessmentResult

        result = self.session.query(AssessmentResult).filter(
            AssessmentResult.assessment_id == assessment_id
        ).first()

        self._cache[assessment_id] = result
        return result

    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get lightweight user summary without loading full objects

        Performance: Only query what's needed, not entire object graph
        """
        from database import User, Assessment

        # Get only necessary fields
        user = self.session.query(
            User.id,
            User.created_at,
            User.last_active
        ).filter(User.id == user_id).first()

        if not user:
            return None

        # Count assessments instead of loading all
        assessment_count = self.session.query(Assessment).filter(
            Assessment.user_id == user_id
        ).count()

        return {
            "user_id": user.id,
            "created_at": user.created_at,
            "last_active": user.last_active,
            "assessment_count": assessment_count
        }


# ============================================================================
# ASYNC OPERATION HELPERS
# ============================================================================

import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for CPU-bound operations
_thread_pool = ThreadPoolExecutor(max_workers=10)

async def run_in_thread(func, *args, **kwargs):
    """
    Run blocking operation in thread pool to prevent blocking event loop

    Use for: Database queries, AI API calls, heavy computations
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_thread_pool, func, *args, **kwargs)


async def generate_ai_report_async(anthropic_client, profile_data: Dict, language: str):
    """
    Generate AI report asynchronously without blocking other requests

    Performance: Allows server to handle other requests while waiting for AI
    """
    from api_main_gdpr import generate_personalized_report

    # Run AI generation in thread pool
    report = await run_in_thread(
        generate_personalized_report,
        profile_data.get("scores", {}),
        profile_data.get("percentiles", {}),
        language
    )

    return report


# ============================================================================
# BACKGROUND JOB PROCESSING
# ============================================================================

import threading
import queue
import time

class BackgroundJobQueue:
    """
    Process heavy tasks in background without blocking API requests

    Use cases:
    - Sending emails
    - Generating PDFs
    - Cleanup tasks
    - Analytics processing
    """

    def __init__(self):
        self.queue = queue.Queue()
        self.worker_thread = None
        self.running = False

    def start(self):
        """Start background worker"""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        print("✅ Background job queue started")

    def stop(self):
        """Stop background worker gracefully"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def _worker(self):
        """Background worker that processes jobs"""
        while self.running:
            try:
                # Get job from queue with timeout
                job_func, args, kwargs = self.queue.get(timeout=1)

                # Execute job
                try:
                    job_func(*args, **kwargs)
                except Exception as e:
                    print(f"Background job error: {e}")
                finally:
                    self.queue.task_done()

            except queue.Empty:
                continue

    def enqueue(self, func, *args, **kwargs):
        """Add job to background queue"""
        self.queue.put((func, args, kwargs))

    def enqueue_audit_log(self, session, user_id: str, action: str, **details):
        """Queue audit log creation as background job"""
        def create_log():
            from database import AuditLog, db
            sess = db.get_session()
            try:
                log = AuditLog(
                    user_id=user_id,
                    action=action,
                    **details
                )
                sess.add(log)
                sess.commit()
            finally:
                sess.close()

        self.enqueue(create_log)

    def enqueue_cleanup(self):
        """Queue database cleanup as background job"""
        def cleanup():
            from database import db
            try:
                db.cleanup_expired_data()
                db.anonymize_old_assessments()
                print(f"✅ Background cleanup completed at {datetime.utcnow()}")
            except Exception as e:
                print(f"❌ Background cleanup failed: {e}")

        self.enqueue(cleanup)


# Global background queue
background_queue = BackgroundJobQueue()


# ============================================================================
# MEMORY OPTIMIZATION
# ============================================================================

def paginate_query(query, page: int = 1, page_size: int = 100):
    """
    Paginate large query results to prevent memory issues

    Performance: Process 1000s of records without loading all into memory
    """
    offset = (page - 1) * page_size
    return query.limit(page_size).offset(offset)


def stream_large_export(session, user_id: str):
    """
    Stream large data exports instead of loading all at once

    Use for: GDPR data exports, large reports
    """
    from database import Assessment

    # Process in batches of 50 assessments
    batch_size = 50
    offset = 0

    while True:
        assessments = session.query(Assessment).filter(
            Assessment.user_id == user_id
        ).limit(batch_size).offset(offset).all()

        if not assessments:
            break

        # Yield batch for processing
        for assessment in assessments:
            yield assessment.to_dict(
                include_questions=False,  # Reduce payload size
                include_answers=True,
                include_result=True
            )

        offset += batch_size


# ============================================================================
# IN-MEMORY CACHING (For systems without Redis)
# ============================================================================

class InMemoryCache:
    """
    Simple in-memory cache with TTL support
    Use Redis in production for multi-instance deployments
    """

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check if expired
        if entry['expires_at'] and datetime.utcnow() > entry['expires_at']:
            del self._cache[key]
            return None

        entry['last_accessed'] = datetime.utcnow()
        entry['hits'] += 1
        return entry['value']

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = 3600):
        """Set value in cache with TTL"""
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        # Evict old entries if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow(),
            'hits': 0
        }

    def delete(self, key: str):
        """Delete entry from cache"""
        if key in self._cache:
            del self._cache[key]

    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (e.g., 'user:123:*')"""
        import fnmatch
        keys_to_delete = [
            key for key in self._cache.keys()
            if fnmatch.fnmatch(key, pattern)
        ]
        for key in keys_to_delete:
            del self._cache[key]

    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self._cache:
            return

        # Find entry with oldest last_accessed
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k]['last_accessed']
        )
        del self._cache[lru_key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_hits = sum(entry['hits'] for entry in self._cache.values())
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'total_hits': total_hits,
            'hit_rate': total_hits / max(1, len(self._cache))
        }

    def clear(self):
        """Clear entire cache"""
        self._cache.clear()


# Global cache instance
app_cache = InMemoryCache(max_size=5000)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_cache_key(prefix: str, *args) -> str:
    """Create consistent cache key from arguments"""
    key_parts = [prefix] + [str(arg) for arg in args]
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def monitor_query_performance(session):
    """
    Monitor slow queries for optimization

    Usage in development to identify bottlenecks
    """
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('sqlalchemy.engine')
    logger.setLevel(logging.INFO)

    # Log queries taking > 100ms
    from sqlalchemy import event

    @event.listens_for(session.bind, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()

    @event.listens_for(session.bind, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - context._query_start_time
        if total > 0.1:  # Log queries > 100ms
            logger.warning(f"Slow query ({total:.2f}s): {statement[:200]}")


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_performance_optimizations():
    """
    Initialize all performance optimizations

    Call this at application startup
    """
    from database import db, DATABASE_URL

    print("🚀 Initializing performance optimizations...")

    # 1. Create optimized database engine
    optimized_engine = create_optimized_engine(DATABASE_URL)
    db.engine = optimized_engine
    db.SessionLocal = sessionmaker(bind=optimized_engine)

    # 2. Create performance indexes
    create_performance_indexes(optimized_engine)

    # 3. Start background job queue
    background_queue.start()

    print("✅ Performance optimizations initialized!")
    print(f"   - Connection pool: {optimized_engine.pool.size()} base + {optimized_engine.pool.overflow} overflow")
    print(f"   - Background queue: Active")
    print(f"   - Database indexes: Created")

    return {
        "engine": optimized_engine,
        "background_queue": background_queue
    }


if __name__ == "__main__":
    # Test performance optimizations
    initialize_performance_optimizations()

    print("\n✅ Performance optimization module ready!")
    print("   Import and use in your application:")
    print("   from performance_optimizations import initialize_performance_optimizations")
    print("   initialize_performance_optimizations()")
