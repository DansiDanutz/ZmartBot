#!/usr/bin/env python3
"""
Telegram routes for KingFisher module
"""

import asyncio
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime

router = APIRouter()

@router.get("/status")
async def get_telegram_status():
    """Get Telegram connection status"""
    return {
        "connected": True,
        "channel": "@KingFisherAutomation",
        "last_message": datetime.now().isoformat(),
        "status": "monitoring"
    }

@router.get("/channel")
async def get_channel_info():
    """Get channel information"""
    return {
        "id": "kingfisher_channel",
        "title": "KingFisher Automation",
        "username": "@KingFisherAutomation",
        "participants_count": 5000,
        "description": "KingFisher automation signals and analysis"
    }

@router.get("/messages")
async def get_recent_messages(limit: int = 10):
    """Get recent messages from channel"""
    # Mock data for now
    messages = []
    for i in range(limit):
        messages.append({
            "id": f"msg_{i}",
            "date": datetime.now().isoformat(),
            "has_media": i % 2 == 0,
            "text": f"KingFisher analysis #{i}",
            "processed": i % 3 == 0
        })
    
    return {
        "messages": messages,
        "total": len(messages),
        "limit": limit
    }

@router.post("/test-connection")
async def test_telegram_connection():
    """Test Telegram API connection"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        result = await telegram_service.test_connection()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@router.post("/start-monitoring")
async def start_monitoring():
    """Start monitoring KingFisher bot"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        await telegram_service.initialize()
        
        # Start monitoring in background
        asyncio.create_task(telegram_service.start_monitoring())
        
        return {
            "success": True,
            "message": "Started monitoring KingFisher bot",
            "bot_id": "5646047866",
            "bot_username": "@thekingfisher_liqmap_bot"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.post("/stop-monitoring")
async def stop_monitoring():
    """Stop monitoring KingFisher bot"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        await telegram_service.stop_monitoring()
        
        return {
            "success": True,
            "message": "Stopped monitoring KingFisher bot"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@router.get("/monitoring-status")
async def get_monitoring_status():
    """Get monitoring status"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        
        return {
            "connected": telegram_service.is_ready(),
            "monitoring": telegram_service.is_monitoring(),
            "bot_id": "5646047866",
            "bot_username": "@thekingfisher_liqmap_bot",
            "last_message_id": telegram_service.last_message_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/process-forwarded")
async def process_forwarded_image(file_id: str, user_id: int, username: str = None):
    """Process manually forwarded image"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        await telegram_service.initialize()
        await telegram_service.process_forwarded_image(file_id, user_id, username)
        
        return {
            "success": True,
            "message": "Processing forwarded image",
            "file_id": file_id,
            "user_id": user_id,
            "username": username
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@router.post("/setup-webhook")
async def setup_webhook(webhook_url: str):
    """Setup webhook for production (requires HTTPS)"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        await telegram_service.initialize()
        success = await telegram_service.setup_webhook(webhook_url)
        
        return {
            "success": success,
            "message": "Webhook setup completed",
            "webhook_url": webhook_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup webhook: {str(e)}")

@router.post("/delete-webhook")
async def delete_webhook():
    """Delete webhook (switch back to polling)"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        await telegram_service.initialize()
        success = await telegram_service.delete_webhook()
        
        return {
            "success": success,
            "message": "Webhook deleted",
            "mode": "polling"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete webhook: {str(e)}")

@router.get("/webhook-info")
async def get_webhook_info():
    """Get current webhook information"""
    try:
        import httpx
        
        bot_token = "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=500, detail="Failed to get webhook info")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get webhook info: {str(e)}")

@router.post("/enable-automation")
async def enable_automation():
    """Enable automation monitoring"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        telegram_service.enable_automation()
        
        return {
            "success": True,
            "message": "Automation enabled",
            "automation_status": "enabled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable automation: {str(e)}")

@router.post("/disable-automation")
async def disable_automation():
    """Disable automation monitoring"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        telegram_service.disable_automation()
        
        return {
            "success": True,
            "message": "Automation disabled",
            "automation_status": "disabled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable automation: {str(e)}")

@router.get("/automation-status")
async def get_automation_status():
    """Get automation status"""
    try:
        from services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        
        return {
            "automation_enabled": telegram_service.is_automation_enabled(),
            "monitoring_active": telegram_service.is_monitoring(),
            "connected": telegram_service.is_ready(),
            "message": "Automation status retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get automation status: {str(e)}") 