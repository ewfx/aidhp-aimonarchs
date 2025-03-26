from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.services.enhanced_recommendation import EnhancedRecommendationService
from app.db.user_operations import UserOperations
from app.db.recommendation_operations import RecommendationOperations
from typing import List, Dict, Any
import logging, json

router = APIRouter(prefix="/enhanced-recommendations", tags=["enhanced-recommendations"])
logger = logging.getLogger(__name__)

# Initialize enhanced recommendation service
recommendation_service = EnhancedRecommendationService()

@router.get("/{user_id}")
async def get_enhanced_recommendations(user_id: str, refresh: bool = False, count: int = 3):
    """
    Get enhanced recommendations for a user.
    If refresh=True, generate new recommendations.
    """
    # Check if user exists
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if refresh:
        # Generate new recommendations
        recommendations = await recommendation_service.generate_recommendations(user_id, count)
        print(recommendations)
        return recommendations
    else:
        # Get existing recommendations
        recommendations = RecommendationOperations.get_user_recommendations(
            user_id=user_id, 
            include_expired=False,
            limit=count
        )
        
        # Convert MongoDB datetime to ISO format string for JSON serialization
        for rec in recommendations:
            if 'timestamp' in rec and hasattr(rec['timestamp'], 'isoformat'):
                rec['timestamp'] = rec['timestamp'].isoformat()
            if 'expires_at' in rec and hasattr(rec['expires_at'], 'isoformat'):
                rec['expires_at'] = rec['expires_at'].isoformat()
        
        return recommendations

@router.post("/{recommendation_id}/refresh")
async def refresh_recommendation(recommendation_id: str):
    """Refresh the content of a specific recommendation"""
    # Check if recommendation exists
    recommendation = RecommendationOperations.get_recommendation_by_id(recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Refresh recommendation
    success = await recommendation_service.refresh_recommendation_content(recommendation_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to refresh recommendation")
    
    # Get updated recommendation
    updated_recommendation = RecommendationOperations.get_recommendation_by_id(recommendation_id)
    
    # Convert MongoDB datetime to ISO format string for JSON serialization
    if 'timestamp' in updated_recommendation and hasattr(updated_recommendation['timestamp'], 'isoformat'):
        updated_recommendation['timestamp'] = updated_recommendation['timestamp'].isoformat()
    if 'expires_at' in updated_recommendation and hasattr(updated_recommendation['expires_at'], 'isoformat'):
        updated_recommendation['expires_at'] = updated_recommendation['expires_at'].isoformat()
    
    return updated_recommendation

@router.post("/compare")
async def compare_recommendations(recommendation_ids: List[str]):
    """Generate a comparison between multiple recommendations"""
    if not recommendation_ids or len(recommendation_ids) < 2:
        raise HTTPException(status_code=400, detail="At least two recommendation IDs are required")
    
    # Generate comparison
    comparison = await recommendation_service.generate_comparison(recommendation_ids)
    
    # Check for errors
    if "error" in comparison:
        raise HTTPException(status_code=500, detail=comparison["error"])
    
    return comparison