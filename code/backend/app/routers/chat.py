from fastapi import APIRouter, HTTPException, Body
from app.db.chat_operations import ChatOperations
from app.db.user_operations import UserOperations
from typing import Dict
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/{user_id}/history")
async def get_chat_history(user_id: str, limit: int = 50):
    """Get chat history for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get latest conversation ID
    conversations = ChatOperations.get_user_conversations(user_id)
    if not conversations:
        # Return empty list if no conversations
        return []
    
    # Get latest conversation
    latest_conversation = conversations[0]
    
    # Get messages for the conversation
    messages = ChatOperations.get_conversation_messages(latest_conversation, limit)
    return messages

@router.post("/{user_id}/message")
async def send_message(
    user_id: str, 
    message: Dict[str, str] = Body(...)
):
    """Send a message to the AI assistant"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get text from message
    text = message.get("message", "")
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Get conversations for user
    conversations = ChatOperations.get_user_conversations(user_id)
    
    # Get or create conversation ID
    conversation_id = conversations[0] if conversations else str(uuid.uuid4())
    
    # Create user message
    user_message = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "sender": "user",
        "text": text,
    }
    
    # Save user message
    ChatOperations.create_message(user_message)
    
    # Here, you'd normally call your AI model to generate a response
    # For the hackathon, we'll use a simple mock response
    
    import random
    
    responses = [
        "Based on your financial profile, I recommend focusing on building your emergency fund before increasing investments.",
        "Looking at your spending patterns, you could optimize your budget by reducing discretionary spending by about 15%.",
        "Your income has increased recently, which presents an opportunity to increase your retirement contributions.",
        "I notice you have several subscription services with overlapping features. Consolidating these could save you $45 monthly."
    ]
    
    # Create assistant message
    assistant_message = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "sender": "assistant",
        "text": random.choice(responses),
    }
    
    # Save assistant message
    message_id = ChatOperations.create_message(assistant_message)
    
    # Get the complete message
    assistant_response = ChatOperations.get_message_by_id(message_id)
    
    return assistant_response