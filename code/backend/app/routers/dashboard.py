from fastapi import APIRouter, HTTPException, Depends
from app.db.user_operations import UserOperations
from app.db.transaction_operations import TransactionOperations
from app.db.recommendation_operations import RecommendationOperations
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/{user_id}")
async def get_dashboard_data(user_id: str):
    # Get user profile
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get top recommendation
    recommendations = RecommendationOperations.get_user_recommendations(user_id, limit=1)
    top_recommendation = recommendations[0] if recommendations else None
    
    # Get spending breakdown
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_summary = TransactionOperations.get_monthly_summary(user_id, current_year, current_month)
    
    # Get income/expenses chart data
    # Create a 6-month history
    chart_data = []
    for i in range(5, -1, -1):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        monthly_data = TransactionOperations.get_monthly_summary(user_id, year, month)
        month_name = datetime(year, month, 1).strftime("%b")
        
        chart_data.append({
            "month": month_name,
            "income": monthly_data["income"],
            "expenses": monthly_data["expenses"]
        })
    
    return {
        "user": user,
        "top_recommendation": top_recommendation,
        "spending_breakdown": monthly_summary["expenses_by_category"],
        "chart_data": chart_data
    }