from fastapi import APIRouter, HTTPException, status
from app.utils.database import recommendations
from app.services.recommendation import RecommendationService
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
            # Generate new recommendations
            new_recommendations = await RecommendationService.generate_recommendations(user_id)
            return new_recommendations
        else:
            # Get existing recommendations
            existing_recommendations = list(recommendations.find({"user_id": user_id}))
            
            # Serialize MongoDB documents
            existing_recommendations = serialize_mongo_doc(existing_recommendations)
                    
            if not existing_recommendations:
                # If no recommendations exist, generate new ones
                new_recommendations = await RecommendationService.generate_recommendations(user_id)
                return new_recommendations
            return existing_recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.post("/{recommendation_id}/feedback", status_code=status.HTTP_200_OK)
async def record_feedback(recommendation_id: str, is_clicked: bool = False):
    """
    Record user feedback on a recommendation
    """
    # Find the recommendation
    recommendation = recommendations.find_one({"recommendation_id": recommendation_id})
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Update feedback
    recommendations.update_one(
        {"recommendation_id": recommendation_id},
        {"$set": {"is_viewed": True, "is_clicked": is_clicked}}
    )
    
    return {"status": "success"}