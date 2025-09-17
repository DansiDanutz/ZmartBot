from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.chat import zmarty_ai

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    user_name: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    user_name: Optional[str] = None

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """Send a message to Zmarty and get a conversational response"""
    response = await zmarty_ai.get_response(request.message, request.user_name)
    
    return ChatResponse(
        response=response,
        user_name=request.user_name
    )