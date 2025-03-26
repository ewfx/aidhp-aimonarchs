from fastapi import APIRouter, HTTPException, Query, Depends
from app.db.transaction_operations import TransactionOperations
from app.db.user_operations import UserOperations
from app.utils.mongo_utils import serialize_mongo_doc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/transactions", tags=["transactions"])

class TransactionCreate(BaseModel):
    amount: float
    description: str
    category: str
    merchant: str
    timestamp: Optional[datetime] = None

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    merchant: Optional[str] = None

@router.get("/{user_id}")
async def get_transactions(
    user_id: str, 
    limit: int = Query(50, ge=1, le=100), 
    skip: int = Query(0, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None
):
    """Get recent transactions for a user with optional filtering"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query parameters
    query_params = {}
    if start_date:
        query_params["start_date"] = start_date
    if end_date:
        query_params["end_date"] = end_date
    if category:
        query_params["category"] = category
    
    # Get transactions
    transactions = TransactionOperations.get_user_transactions(
        user_id=user_id,
        limit=limit,
        skip=skip,
        sort_by="timestamp",
        sort_order=-1,
        **query_params
    )
    
    # Serialize the MongoDB documents
    serialized_transactions = serialize_mongo_doc(transactions)
    return serialized_transactions

@router.get("/{user_id}/analytics")
async def get_transaction_analytics(user_id: str, months: int = Query(6, ge=1, le=24)):
    """Get transaction analytics for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Get monthly summaries for the past X months
    monthly_data = []
    for i in range(months - 1, -1, -1):
        # Calculate month and year
        month = (current_month - i) % 12
        if month == 0:
            month = 12
        year = current_year - ((current_month - i) // 12)
        
        # Get monthly summary
        summary = TransactionOperations.get_monthly_summary(user_id, year, month)
        month_name = datetime(year, month, 1).strftime("%b")
        
        monthly_data.append({
            "month": month_name,
            "income": summary["income"],
            "expenses": summary["expenses"],
            "net": summary["net"]
        })
    
    # Get category spending trends
    categories = ["Groceries", "Dining", "Entertainment", "Utilities", "Shopping", "Transportation"]
    category_trends = {}
    
    for category in categories:
        trend = TransactionOperations.get_category_spending_trend(
            user_id, category, months
        )
        category_trends[category] = trend
    
    return {
        "monthly_data": monthly_data,
        "category_trends": category_trends
    }

@router.get("/{user_id}/sentiment")
async def get_sentiment(user_id: str):
    """Get sentiment analysis for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return sentiment from user profile
    sentiment = user.get("sentiment", {
        "overall_sentiment": "neutral",
        "confidence": 0.5,
        "financial_health": "stable",
        "last_updated": datetime.now()
    })
    
    # Serialize to handle datetime objects
    serialized_sentiment = serialize_mongo_doc(sentiment)
    
    return {
        "user_id": user_id,
        "sentiment_analysis": serialized_sentiment
    }

@router.get("/{user_id}/anomalies")
async def get_anomalies(user_id: str, days: int = Query(30, ge=1, le=90)):
    """Get spending anomalies for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get anomalies from user profile
    anomalies = user.get("anomalies", [])
    
    # Filter by detection date if needed
    if days < 90:
        cutoff_date = datetime.now() - timedelta(days=days)
        anomalies = [
            anomaly for anomaly in anomalies 
            if anomaly.get("detection_date", datetime.now()) >= cutoff_date
        ]
    
    # Serialize to handle datetime objects
    serialized_anomalies = serialize_mongo_doc(anomalies)
    
    return serialized_anomalies

@router.get("/{user_id}/predicted-expenses")
async def get_predicted_expenses(user_id: str):
    """Get predicted upcoming expenses for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get predicted expenses from user profile
    predicted_expenses = user.get("predicted_expenses", [])
    
    # Only return future expenses
    now = datetime.now()
    future_expenses = [
        expense for expense in predicted_expenses 
        if expense.get("due_date", now) > now
    ]
    
    # Serialize to handle datetime objects
    serialized_expenses = serialize_mongo_doc(future_expenses)
    
    return serialized_expenses

@router.post("/{user_id}")
async def create_transaction(user_id: str, transaction: TransactionCreate):
    """Create a new transaction for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare transaction data
    transaction_data = transaction.dict()
    transaction_data["user_id"] = user_id
    
    # If timestamp not provided, use current time
    if not transaction_data.get("timestamp"):
        transaction_data["timestamp"] = datetime.now()
    
    # Create transaction
    transaction_id = TransactionOperations.create_transaction(transaction_data)
    
    # Return created transaction
    created_transaction = TransactionOperations.get_transaction_by_id(transaction_id)
    if not created_transaction:
        raise HTTPException(status_code=500, detail="Failed to create transaction")
    
    return serialize_mongo_doc(created_transaction)

@router.put("/{transaction_id}")
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    """Update a transaction"""
    # Check if transaction exists
    existing_transaction = TransactionOperations.get_transaction_by_id(transaction_id)
    if not existing_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update transaction
    update_data = {k: v for k, v in transaction.dict().items() if v is not None}
    success = TransactionOperations.update_transaction(transaction_id, update_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update transaction")
    
    # Return updated transaction
    updated_transaction = TransactionOperations.get_transaction_by_id(transaction_id)
    return serialize_mongo_doc(updated_transaction)

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Delete a transaction"""
    # Check if transaction exists
    existing_transaction = TransactionOperations.get_transaction_by_id(transaction_id)
    if not existing_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Delete transaction
    success = TransactionOperations.delete_transaction(transaction_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete transaction")
    
    return {"status": "success", "message": "Transaction deleted"}

@router.get("/{user_id}/categories")
async def get_transaction_categories(user_id: str):
    """Get all transaction categories used by a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get unique categories
    categories = TransactionOperations.get_user_categories(user_id)
    
    return categories

@router.get("/{user_id}/summary")
async def get_summary(user_id: str, period: str = Query("month", regex="^(month|year|week)$")):
    """Get a summary of transactions for a specific period"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    now = datetime.now()
    
    # Define time period
    if period == "week":
        # Get transactions for current week
        start_date = now - timedelta(days=now.weekday())
        start_date = datetime(start_date.year, start_date.month, start_date.day)
        end_date = now
    elif period == "month":
        # Get transactions for current month
        start_date = datetime(now.year, now.month, 1)
        end_date = now
    else:  # year
        # Get transactions for current year
        start_date = datetime(now.year, 1, 1)
        end_date = now
    
    # Get transactions for the period
    transactions = TransactionOperations.get_user_transactions_in_date_range(
        user_id, start_date, end_date
    )
    
    # Calculate total income and expenses
    income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
    
    # Group expenses by category
    expenses_by_category = {}
    for transaction in transactions:
        if transaction["amount"] < 0:
            category = transaction.get("category", "Uncategorized")
            expenses_by_category[category] = expenses_by_category.get(category, 0) + abs(transaction["amount"])
    
    return {
        "user_id": user_id,
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "income": income,
        "expenses": expenses,
        "net": income - expenses,
        "transaction_count": len(transactions),
        "expenses_by_category": expenses_by_category
    }