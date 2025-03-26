from fastapi import APIRouter, HTTPException, Body, Depends, BackgroundTasks, Query
from app.db.chat_operations import ChatOperations
from app.db.user_operations import UserOperations
from app.db.transaction_operations import TransactionOperations
from app.services.genai_services import GenAIService
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import logging
import asyncio
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Initialize GenAI service
genai_service = GenAIService()

MAX_HISTORY_MESSAGES = 10  # Maximum number of messages to include in context

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
    message: Dict[str, str] = Body(...),
    background_tasks: BackgroundTasks = None
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
        "timestamp": datetime.now()
    }
    
    # Save user message
    user_message_id = ChatOperations.create_message(user_message)
    
    # Get conversation history for context
    chat_history = ChatOperations.get_conversation_messages(
        conversation_id, 
        limit=MAX_HISTORY_MESSAGES
    )
    
    # Get transaction history for context
    transaction_history = TransactionOperations.get_user_transactions(
        user_id=user_id,
        limit=20,
        sort_by="timestamp",
        sort_order=-1
    )
    
    try:
        # Generate AI response using GenAI service
        ai_response = await genai_service.generate_financial_advice(
            user_profile=user,
            user_query=text,
            transaction_history=transaction_history,
            chat_history=chat_history
        )
        # print("AI RESPONSE", ai_response.text.candidates[0].content.parts[0].text)
        # Create assistant message
        assistant_message = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "sender": "assistant",
            "text": ai_response,
            "timestamp": datetime.now(),
            "context": {
                "previous_message_id": user_message_id
            },
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "genai_generated": True
            }
        }
        print("HERE 1")
        # Save assistant message
        # message_id = ChatOperations.create_message(assistant_message)
        
        # Get the complete message
        # assistant_response = ChatOperations.get_message_by_id(message_id)
        print("ASSISTANT RESPINSE",assistant_message)
        # If background tasks available, run analysis task
        if background_tasks:
            background_tasks.add_task(analyze_chat_message, user_id, text, ai_response)
        
        print("returning")
        return assistant_message
        
    except Exception as e:
        # Log the error
        logger.error(f"Error generating AI response: {str(e)}")
        
        # Create a fallback response
        fallback_message = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "sender": "assistant",
            "text": "I'm sorry, I encountered an issue while processing your request. Could you please try again?",
            "timestamp": datetime.now(),
            "context": {
                "previous_message_id": user_message_id,
                "error": str(e)
            }
        }
        
        # Save fallback message
        message_id = ChatOperations.create_message(fallback_message)
        
        # Get the complete message
        fallback_response = ChatOperations.get_message_by_id(message_id)
        
        return fallback_message
    

@router.get("/{user_id}/message/stream")
async def send_message_streaming(
    user_id: str, 
    message: str = Query(..., description="Message text")
):  
    """Send a message to the AI assistant with streaming response"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get text from message
    if not message:
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
        "text": message,
        "timestamp": datetime.now()
    }
    
    # Save user message
    user_message_id = ChatOperations.create_message(user_message)
    assistant_message = ''
    # Get conversation history for context
    chat_history = ChatOperations.get_conversation_messages(
        conversation_id, 
        limit=MAX_HISTORY_MESSAGES
    )
    
    # Get transaction history for context
    transaction_history = TransactionOperations.get_user_transactions(
        user_id=user_id,
        limit=20,
        sort_by="timestamp",
        sort_order=-1
    )
    try:
        # Generate response (non-streaming for now)
        full_response = await genai_service.generate_financial_advice(
            user_profile=user,
            user_query=message,
            transaction_history=transaction_history,
            chat_history=chat_history
        )
        print("FULL RESPONSE", type(full_response))
        
        # Split response into words
        words = str(full_response).split()
        
        # Stream response in small chunks
        for i in range(0, len(words), 2):
            chunk = ' '.join(words[i:i+2])
            yield f"data: {chunk}\n\n"  # Corrected format for SSE
            await asyncio.sleep(0.2)  # Simulate delay
        
        # Final event to signal completion
        yield f"data: [DONE]\n\n"
        
        # Save complete response in database
        assistant_message = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "sender": "assistant",
            "text": full_response,
            "timestamp": datetime.now(),
            "context": {
                "previous_message_id": user_message_id
            },
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "genai_generated": True,
                "streamed": True
            }
        }
        print(assistant_message)
        # Save assistant message
        ChatOperations.create_message(assistant_message)
        # return assistant_message
    except Exception as e:
        logger.error(f"Error in streaming response: {str(e)}")
        yield f"data: I'm sorry, I encountered an issue while processing your request.\n\n"
        yield f"data: [DONE]\n\n"
        
        # Save error message
        error_message = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "sender": "assistant",
            "text": "I'm sorry, I encountered an issue while processing your request. Could you please try again?",
            "timestamp": datetime.now(),
            "context": {
                "previous_message_id": user_message_id,
                "error": str(e)
            }
        }
        
        ChatOperations.create_message(error_message)
        # return error_message


async def analyze_chat_message(user_id: str, user_message: str, ai_response: str):
    """
    Background task to analyze chat messages for insights
    
    Args:
        user_id: User ID
        user_message: Original user message
        ai_response: AI generated response
    """
    try:
        # This would analyze the chat for potential insights or actions
        # For example, if the user asks about saving for a home, we might want to:
        # 1. Update user's financial goals
        # 2. Generate home purchase-related recommendations
        # 3. Track interest in specific product categories
        
        # Simple intent detection (in a real system, this would use NLP/GenAI)
        intents = {
            "saving": ["save", "saving", "savings", "emergency fund"],
            "investing": ["invest", "investing", "investment", "stock", "bond"],
            "debt": ["debt", "loan", "credit card", "mortgage"],
            "retirement": ["retire", "retirement", "401k", "ira"],
            "budgeting": ["budget", "spending", "expense", "track"]
        }
        
        detected_intents = []
        user_message_lower = user_message.lower()
        
        for intent, keywords in intents.items():
            if any(keyword in user_message_lower for keyword in keywords):
                detected_intents.append(intent)
        
        if detected_intents:
            logger.info(f"Detected intents in user message: {detected_intents}")
            
            # Here you would take actions based on detected intents
            # For example, updating user preferences or suggesting recommendations
            
            # Just logging for now
            logger.info(f"Processing intents for user {user_id}: {detected_intents}")
            
    except Exception as e:
        logger.error(f"Error in message analysis: {str(e)}")