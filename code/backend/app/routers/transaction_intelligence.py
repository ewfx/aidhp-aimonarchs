# app/routers/transaction_intelligence.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.transaction_intelligence import TransactionIntelligenceService
from app.db.user_operations import UserOperations
from typing import List, Dict, Any
import logging
from datetime import datetime

router = APIRouter(prefix="/transaction-intelligence", tags=["transaction-intelligence"])
logger = logging.getLogger(__name__)

# Initialize transaction intelligence service
transaction_intelligence_service = TransactionIntelligenceService()

@router.get("/{user_id}/anomalies")
async def get_anomalies(user_id: str, refresh: bool = False):
    """Get spending anomalies for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If refresh requested, generate new anomalies
    if refresh:
        anomalies = await transaction_intelligence_service.detect_anomalies(user_id)
        return anomalies
    
    # Otherwise, return existing anomalies from user profile
    anomalies = user.get("anomalies", [])
    
    # Convert MongoDB datetime to ISO format string for JSON serialization
    for anomaly in anomalies:
        if 'detection_date' in anomaly and hasattr(anomaly['detection_date'], 'isoformat'):
            anomaly['detection_date'] = anomaly['detection_date'].isoformat()
    
    return anomalies

@router.get("/{user_id}/predicted-expenses")
async def get_predicted_expenses(user_id: str, refresh: bool = False):
    """Get predicted upcoming expenses for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If refresh requested, generate new predictions
    if refresh:
        predicted_expenses = await transaction_intelligence_service.predict_expenses(user_id)
        return predicted_expenses
    
    # Otherwise, return existing predictions from user profile
    predicted_expenses = user.get("predicted_expenses", [])
    
    # Filter to only future expenses
    now = datetime.now()
    future_expenses = [
        expense for expense in predicted_expenses 
        if expense.get("due_date", now) > now
    ]
    
    # Convert MongoDB datetime to ISO format string for JSON serialization
    for expense in future_expenses:
        if 'due_date' in expense and hasattr(expense['due_date'], 'isoformat'):
            expense['due_date'] = expense['due_date'].isoformat()
    
    return future_expenses

@router.get("/{user_id}/spending-patterns")
async def get_spending_patterns(user_id: str):
    """Get spending pattern analysis for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Analyze spending patterns
    patterns = await transaction_intelligence_service.analyze_spending_patterns(user_id)
    
    # Convert MongoDB datetime to ISO format string for JSON serialization
    if 'start_date' in patterns and hasattr(patterns['start_date'], 'isoformat'):
        patterns['start_date'] = patterns['start_date'].isoformat()
    if 'end_date' in patterns and hasattr(patterns['end_date'], 'isoformat'):
        patterns['end_date'] = patterns['end_date'].isoformat()
    
    return patterns

@router.post("/{user_id}/acknowledge-anomaly/{anomaly_id}")
async def acknowledge_anomaly(user_id: str, anomaly_id: str):
    """Mark an anomaly as acknowledged"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find and update the anomaly
    anomalies = user.get("anomalies", [])
    updated = False
    
    for anomaly in anomalies:
        if anomaly.get("anomaly_id") == anomaly_id:
            anomaly["is_acknowledged"] = True
            updated = True
            break
    
    if not updated:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    # Update user profile
    success = UserOperations.update_user(user_id, {"anomalies": anomalies})
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update anomaly")
    
    return {"status": "success"}

@router.get("/{user_id}/monthly-report/{year}/{month}")
async def get_monthly_report(user_id: str, year: int, month: int):
    """Get a monthly financial report"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify valid month and year
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid month")
    
    # Generate monthly report
    report = await transaction_intelligence_service.generate_monthly_report(user_id, year, month)
    
    return report