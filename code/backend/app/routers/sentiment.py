from fastapi import APIRouter, HTTPException, status
from app.utils.database import transactions
from app.services.sentiment_service import SentimentService
from typing import Dict, Any

router = APIRouter(
    prefix="/sentiment",
    tags=["sentiment"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{user_id}")
async def analyze_user_sentiment(user_id: str):
    """
    Analyze financial sentiment based on user transactions
    """
    # Get user transactions
    user_transactions = list(transactions.find({"user_id": user_id}).sort("timestamp", -1).limit(50))
    
    if not user_transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transaction data found for user"
        )
    
    # Initialize sentiment service
    sentiment_service = SentimentService()
    
    # Analyze sentiment
    sentiment_result = sentiment_service.analyze_transaction_sentiment(user_transactions)
    
    # Return results
    return {
        "user_id": user_id,
        "sentiment_analysis": sentiment_result,
        "transaction_count": len(user_transactions)
    }