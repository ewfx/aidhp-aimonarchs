from fastapi import APIRouter, HTTPException, status
from app.utils.database import recommendations
from app.services.recommendation import RecommendationService
from app.db.recommendation_operations import RecommendationOperations
from app.db.user_operations import UserOperations
from app.utils.mongo_utils import serialize_mongo_doc
from typing import List

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{user_id}")
async def get_recommendations(user_id: str, refresh: bool = False):
    """
    Get recommendations for a user.
    If refresh=True, generate new recommendations.
    """
    
    try:
        if refresh:
            # Generate new recommendations - this should be an async function
            # Make sure RecommendationService.generate_recommendations is async
            new_recommendations = await RecommendationService.generate_recommendations(user_id)
            return new_recommendations
        else:
            # Get existing recommendations - This is NOT an async operation, don't use await here
            existing_recommendations = list(recommendations.find({"user_id": user_id}))
            
            # Serialize MongoDB documents
            existing_recommendations = serialize_mongo_doc(existing_recommendations)
                    
            if not existing_recommendations:
                # If no recommendations exist, generate new ones
                # Make sure RecommendationService.generate_recommendations is async
                new_recommendations = await RecommendationService.generate_recommendations(user_id)
                return new_recommendations
            
            return existing_recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.post("/{recommendation_id}/feedback", status_code=status.HTTP_200_OK)
async def submit_feedback(recommendation_id: str, is_helpful: bool = False):
    """Submit feedback for a recommendation"""
    success = RecommendationOperations.record_recommendation_feedback(
        recommendation_id, is_helpful
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return {"status": "success"}