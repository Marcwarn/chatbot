"""
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
