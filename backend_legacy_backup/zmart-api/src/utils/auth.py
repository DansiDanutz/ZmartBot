#!/usr/bin/env python3
"""
Simple auth utilities for development
"""

from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Simple bearer token security
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    """
    Get current user from token (simplified for development)
    
    Returns:
        User dict with basic info
    """
    # For development, return a mock user
    # In production, validate JWT token and get real user
    return {
        "username": "admin",
        "role": "admin",
        "user_id": "dev-user-001"
    }

# Export for use in routes
__all__ = ['get_current_user']