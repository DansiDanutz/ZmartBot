#!/usr/bin/env python3
"""
KingFisher Cache Manager Stub
This is a placeholder for the KingFisher cache manager.
The actual implementation is in the kingfisher-module.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class KingFisherCacheManager:
    """Stub for KingFisher cache manager"""
    
    def __init__(self):
        logger.info("KingFisher cache manager stub initialized")
        self.enabled = False
    
    async def get(self, category: str, symbol: str, image_type: str) -> Optional[Any]:
        """Stub get method"""
        return None
    
    async def connect(self):
        """Stub connect method"""
        pass
    
    async def disconnect(self):
        """Stub disconnect method"""
        pass
    
    def get_statistics(self) -> dict:
        """Stub statistics method"""
        return {
            'enabled': False,
            'message': 'KingFisher cache not available in this module'
        }

# Create singleton instance
kingfisher_cache = KingFisherCacheManager()