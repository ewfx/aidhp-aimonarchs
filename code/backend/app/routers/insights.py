from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.insights_service import InsightsService
from app.db.user_operations import UserOperations
from typing import List, Dict, Any
import logging

router = APIRouter(prefix="/insights", tags=["insights"])
logger = logging.getLogger(__name__)

# Initialize insights service
insights_service = InsightsService()

@router.get("/{user_id}")
async def get_user_insights(user_id: str):
    """Get insights for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get insights from user profile
    insights = user.get("insights", [])
    
    # Sort by importance and creation date
    def sort_key(insight):
        # Convert importance to numeric value
        importance_values = {"high": 3, "medium": 2, "low": 1}
        return (importance_values.get(insight.get("importance", "medium"), 2), 
                insight.get("created_at", ""))
    
    sorted_insights = sorted(insights, key=sort_key, reverse=True)
    
    # Convert MongoDB datetime to ISO format string for JSON serialization
    for insight in sorted_insights:
        if 'created_at' in insight and hasattr(insight['created_at'], 'isoformat'):
            insight['created_at'] = insight['created_at'].isoformat()
        if 'expires_at' in insight and hasattr(insight['expires_at'], 'isoformat'):
            insight['expires_at'] = insight['expires_at'].isoformat()
    
    return sorted_insights

@router.post("/{user_id}/refresh")
async def refresh_user_insights(user_id: str, background_tasks: BackgroundTasks):
    """Generate fresh insights for a user"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate insights in the background
    background_tasks.add_task(insights_service.generate_user_insights, user_id)
    
    return {"status": "Insight generation started", "user_id": user_id}

@router.post("/{user_id}/insight/{insight_id}/read")
async def mark_insight_as_read(user_id: str, insight_id: str):
    """Mark an insight as read"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mark as read
    success = insights_service.mark_insight_read(user_id, insight_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    return {"status": "success"}

@router.post("/{user_id}/insight/{insight_id}/action")
async def record_insight_action(user_id: str, insight_id: str, acted_upon: bool = True):
    """Record whether a user acted upon an insight"""
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Record action
    success = insights_service.record_insight_action(user_id, insight_id, acted_upon)
    
    if not success:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    return {"status": "success"}

# Admin-only endpoint for refreshing all user insights
@router.post("/admin/refresh-all")
async def refresh_all_insights(background_tasks: BackgroundTasks):
    """Background job to refresh insights for all users (admin only)"""
    # In a real app, this would require admin authentication
    
    # Start background task
    background_tasks.add_task(insights_service.refresh_all_user_insights)
    
    return {"status": "Insight refresh started for all users"}