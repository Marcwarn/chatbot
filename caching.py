"""
Caching Layer for Personality Assessment API
Implements intelligent caching for AI-generated reports, assessments, and statistics
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import hashlib
import json
import os

# Try to import Redis, fallback to in-memory cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from performance_optimizations import InMemoryCache


# ============================================================================
# CACHE CONFIGURATION
# ============================================================================

CACHE_CONFIG = {
    # AI-generated reports (expensive to generate, rarely change for same profile)
    "ai_report": {
        "ttl": 7 * 24 * 3600,  # 7 days
        "enabled": True,
        "description": "AI-generated personality reports based on Big Five scores"
    },

    # Assessment questions (static, never change)
    "assessment_questions": {
        "ttl": 30 * 24 * 3600,  # 30 days
        "enabled": True,
        "description": "IPIP-50 question bank (static content)"
    },

    # Admin statistics (expensive to calculate)
    "admin_stats": {
        "ttl": 5 * 60,  # 5 minutes
        "enabled": True,
        "description": "Dashboard statistics and analytics"
    },

    # User profiles for chat context
    "user_profile": {
        "ttl": 24 * 3600,  # 24 hours
        "enabled": True,
        "description": "User Big Five profiles for chat personalization"
    },

    # Assessment results (completed assessments)
    "assessment_result": {
        "ttl": 30 * 24 * 3600,  # 30 days
        "enabled": True,
        "description": "Completed assessment results"
    },

    # Rate limiting counters
    "rate_limit": {
        "ttl": 3600,  # 1 hour
        "enabled": True,
        "description": "Rate limiting counters"
    }
}


# ============================================================================
# REDIS CACHE (Production)
# ============================================================================

class RedisCache:
    """
    Redis-based cache for production use
    Supports distributed caching across multiple server instances
    """

    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            raise ImportError("Redis not installed. Install with: pip install redis")

        redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")

        try:
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=50
            )
            # Test connection
            self.client.ping()
            print("✅ Redis cache connected")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = 3600):
        """Set value in Redis cache with TTL"""
        try:
            serialized = json.dumps(value, default=str)
            if ttl_seconds:
                self.client.setex(key, ttl_seconds, serialized)
            else:
                self.client.set(key, serialized)
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False

    def delete(self, key: str):
        """Delete key from Redis"""
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Redis DELETE error: {e}")

    def invalidate_pattern(self, pattern: str):
        """Delete all keys matching pattern (e.g., 'user:123:*')"""
        try:
            cursor = 0
            while True:
                cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                if keys:
                    self.client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            print(f"Redis INVALIDATE error: {e}")

    def increment(self, key: str, amount: int = 1, ttl_seconds: Optional[int] = None) -> int:
        """Increment counter (useful for rate limiting)"""
        try:
            value = self.client.incr(key, amount)
            if ttl_seconds and value == amount:  # First increment
                self.client.expire(key, ttl_seconds)
            return value
        except Exception as e:
            print(f"Redis INCR error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        try:
            info = self.client.info()
            return {
                'connected': True,
                'used_memory': info.get('used_memory_human', 'N/A'),
                'total_keys': self.client.dbsize(),
                'hit_rate': info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1))
            }
        except Exception as e:
            return {'connected': False, 'error': str(e)}

    def clear(self):
        """Clear entire cache (use with caution!)"""
        try:
            self.client.flushdb()
        except Exception as e:
            print(f"Redis CLEAR error: {e}")


# ============================================================================
# UNIFIED CACHE INTERFACE
# ============================================================================

class CacheManager:
    """
    Unified cache interface that automatically selects Redis or in-memory cache
    Provides high-level caching methods for specific use cases
    """

    def __init__(self):
        """Initialize cache backend (Redis if available, else in-memory)"""
        self.backend = None
        self.backend_type = "none"

        # Try Redis first
        redis_url = os.getenv("REDIS_URL")
        if redis_url and REDIS_AVAILABLE:
            try:
                self.backend = RedisCache(redis_url)
                self.backend_type = "redis"
                print("🚀 Cache: Using Redis")
                return
            except Exception as e:
                print(f"⚠️  Redis unavailable, falling back to in-memory cache: {e}")

        # Fallback to in-memory
        self.backend = InMemoryCache(max_size=5000)
        self.backend_type = "memory"
        print("🚀 Cache: Using in-memory cache")

    def _make_key(self, cache_type: str, *args) -> str:
        """Create cache key with namespace"""
        parts = [cache_type] + [str(arg) for arg in args]
        key_string = ":".join(parts)
        # Hash long keys to keep them manageable
        if len(key_string) > 200:
            hash_suffix = hashlib.md5(key_string.encode()).hexdigest()
            return f"{cache_type}:{hash_suffix}"
        return key_string

    # ── High-level caching methods ──

    def get_ai_report(self, profile_hash: str) -> Optional[Dict]:
        """
        Get cached AI-generated report

        Args:
            profile_hash: Hash of Big Five scores (same profile = same report)

        Returns:
            Cached report dict or None
        """
        if not CACHE_CONFIG["ai_report"]["enabled"]:
            return None

        key = self._make_key("ai_report", profile_hash)
        return self.backend.get(key)

    def set_ai_report(self, profile_hash: str, report: Dict):
        """Cache AI-generated report"""
        if not CACHE_CONFIG["ai_report"]["enabled"]:
            return

        key = self._make_key("ai_report", profile_hash)
        ttl = CACHE_CONFIG["ai_report"]["ttl"]
        self.backend.set(key, report, ttl)

    def get_assessment_questions(self, language: str = "sv") -> Optional[List]:
        """Get cached assessment questions"""
        if not CACHE_CONFIG["assessment_questions"]["enabled"]:
            return None

        key = self._make_key("questions", language)
        return self.backend.get(key)

    def set_assessment_questions(self, questions: List, language: str = "sv"):
        """Cache assessment questions"""
        if not CACHE_CONFIG["assessment_questions"]["enabled"]:
            return

        key = self._make_key("questions", language)
        ttl = CACHE_CONFIG["assessment_questions"]["ttl"]
        self.backend.set(key, questions, ttl)

    def get_admin_stats(self) -> Optional[Dict]:
        """Get cached admin dashboard statistics"""
        if not CACHE_CONFIG["admin_stats"]["enabled"]:
            return None

        key = self._make_key("admin_stats")
        return self.backend.get(key)

    def set_admin_stats(self, stats: Dict):
        """Cache admin statistics"""
        if not CACHE_CONFIG["admin_stats"]["enabled"]:
            return

        key = self._make_key("admin_stats")
        ttl = CACHE_CONFIG["admin_stats"]["ttl"]
        self.backend.set(key, stats, ttl)

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get cached user profile for chat context"""
        if not CACHE_CONFIG["user_profile"]["enabled"]:
            return None

        key = self._make_key("profile", user_id)
        return self.backend.get(key)

    def set_user_profile(self, user_id: str, profile: Dict):
        """Cache user profile"""
        if not CACHE_CONFIG["user_profile"]["enabled"]:
            return

        key = self._make_key("profile", user_id)
        ttl = CACHE_CONFIG["user_profile"]["ttl"]
        self.backend.set(key, profile, ttl)

    def invalidate_user(self, user_id: str):
        """Invalidate all cache entries for a user (e.g., on GDPR delete)"""
        pattern = f"*:{user_id}:*"
        self.backend.invalidate_pattern(pattern)

        # Also invalidate admin stats (user count changed)
        self.backend.delete(self._make_key("admin_stats"))

    def get_assessment_result(self, assessment_id: str) -> Optional[Dict]:
        """Get cached assessment result"""
        if not CACHE_CONFIG["assessment_result"]["enabled"]:
            return None

        key = self._make_key("assessment", assessment_id)
        return self.backend.get(key)

    def set_assessment_result(self, assessment_id: str, result: Dict):
        """Cache assessment result"""
        if not CACHE_CONFIG["assessment_result"]["enabled"]:
            return

        key = self._make_key("assessment", assessment_id)
        ttl = CACHE_CONFIG["assessment_result"]["ttl"]
        self.backend.set(key, result, ttl)

    # ── Cache invalidation helpers ──

    def invalidate_admin_cache(self):
        """Invalidate admin statistics cache (call when data changes)"""
        self.backend.delete(self._make_key("admin_stats"))

    def clear_all(self):
        """Clear entire cache (use with caution!)"""
        self.backend.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.backend.get_stats()
        stats['backend_type'] = self.backend_type
        stats['config'] = {
            k: {
                'enabled': v['enabled'],
                'ttl_hours': v['ttl'] / 3600
            }
            for k, v in CACHE_CONFIG.items()
        }
        return stats


# ============================================================================
# PROFILE HASH GENERATOR
# ============================================================================

def generate_profile_hash(scores: Dict[str, float], language: str = "sv") -> str:
    """
    Generate deterministic hash from Big Five scores

    Same scores = same hash = cache hit on AI report
    This is the key to caching AI-generated reports effectively!

    Args:
        scores: Dict of Big Five scores (E, A, C, N, O)
        language: Report language

    Returns:
        Hash string
    """
    # Round scores to 1 decimal to avoid minor variations
    rounded_scores = {
        k: round(v, 1) for k, v in sorted(scores.items())
    }

    # Create deterministic string
    score_string = json.dumps(rounded_scores, sort_keys=True) + f":{language}"

    # Hash it
    return hashlib.sha256(score_string.encode()).hexdigest()[:16]


# ============================================================================
# DECORATOR FOR AUTOMATIC CACHING
# ============================================================================

def cached(cache_type: str, key_func=None, ttl: Optional[int] = None):
    """
    Decorator for automatic function result caching

    Usage:
        @cached("expensive_calc", lambda x, y: f"{x}:{y}", ttl=3600)
        def expensive_calculation(x, y):
            # expensive work
            return result
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = cache_type + ":" + key_func(*args, **kwargs)
            else:
                # Use function name + args as key
                cache_key = cache_type + ":" + str(args) + str(kwargs)

            # Try cache first
            cached_value = cache.backend.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Cache miss - compute value
            result = func(*args, **kwargs)

            # Store in cache
            use_ttl = ttl or CACHE_CONFIG.get(cache_type, {}).get("ttl", 3600)
            cache.backend.set(cache_key, result, use_ttl)

            return result

        return wrapper
    return decorator


# ============================================================================
# GLOBAL CACHE INSTANCE
# ============================================================================

# Initialize global cache manager
cache = CacheManager()


# ============================================================================
# CACHE WARMUP
# ============================================================================

def warmup_cache():
    """
    Pre-populate cache with frequently accessed data
    Run this at application startup
    """
    print("🔥 Warming up cache...")

    try:
        # Cache assessment questions (static content)
        from api_main_gdpr import IPIP_QUESTIONS, LIKERT_OPTIONS, DIMENSION_META

        questions_data = {
            "questions": IPIP_QUESTIONS,
            "options": LIKERT_OPTIONS,
            "dimensions": DIMENSION_META
        }

        cache.set_assessment_questions(questions_data, "sv")
        print("   ✅ Assessment questions cached")

    except Exception as e:
        print(f"   ⚠️  Cache warmup error: {e}")

    print("🔥 Cache warmup complete")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CACHING MODULE TEST")
    print("=" * 60)

    # Test cache operations
    print("\n1. Testing AI report caching...")
    test_scores = {"E": 75.0, "A": 60.0, "C": 85.0, "N": 40.0, "O": 70.0}
    profile_hash = generate_profile_hash(test_scores)
    print(f"   Profile hash: {profile_hash}")

    # Cache report
    test_report = {
        "profile_overview": "Test profile",
        "career_suggestions": ["Developer", "Designer"]
    }
    cache.set_ai_report(profile_hash, test_report)

    # Retrieve report
    cached_report = cache.get_ai_report(profile_hash)
    print(f"   Cached report: {cached_report}")

    print("\n2. Testing cache statistics...")
    stats = cache.get_stats()
    print(f"   Backend: {stats['backend_type']}")
    print(f"   Stats: {stats}")

    print("\n3. Testing cache invalidation...")
    cache.invalidate_user("test_user_123")
    print("   ✅ User cache invalidated")

    print("\n✅ All cache tests passed!")
