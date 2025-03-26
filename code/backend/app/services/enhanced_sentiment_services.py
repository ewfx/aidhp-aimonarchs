from typing import List, Dict, Any
from datetime import datetime
import logging
import asyncio

from app.db.user_operations import UserOperations
from app.services.genai_services import GenAIService

logger = logging.getLogger(__name__)

class EnhancedSentimentService:
    """
    Enhanced sentiment analysis service using GenAI
    This replaces the rule-based approach with more nuanced AI-driven analysis
    """
    
    def __init__(self):
        """Initialize sentiment service with GenAI service"""
        self.genai_service = GenAIService()
        
    async def analyze_transaction_sentiment(self, 
                                     transactions: List[Dict[str, Any]], 
                                     user_id: str = None) -> Dict[str, Any]:
        """
        Analyze financial sentiment from transaction data
        
        Args:
            transactions: List of user transactions
            user_id: Optional user ID for updating user profile
            
        Returns:
            Dict with sentiment analysis results
        """
        if not transactions:
            return {
                "overall_sentiment": "neutral",
                "confidence": 0.5,
                "financial_health": "stable",
                "explanation": "Not enough transaction data to analyze."
            }
        
        try:
            # Analyze sentiment using GenAI
            sentiment_analysis = await self.genai_service.analyze_sentiment(transactions)
            
            # Add timestamp to the analysis
            sentiment_analysis["analysis_date"] = datetime.now()
            
            # Update user profile if user_id is provided
            if user_id:
                await self._update_user_sentiment(user_id, sentiment_analysis)
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            
            # Fallback to a basic analysis
            return {
                "overall_sentiment": "neutral",
                "confidence": 0.5,
                "financial_health": "stable",
                "explanation": "Could not perform detailed analysis.",
                "error": str(e)
            }
    
    async def generate_financial_health_report(self, 
                                      user_id: str, 
                                      time_period: str = "month") -> Dict[str, Any]:
        """
        Generate a detailed financial health report
        
        Args:
            user_id: User ID
            time_period: Time period for analysis (week, month, quarter, year)
            
        Returns:
            Dict with financial health report
        """
        try:
            # Get user profile
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get user transactions (this would typically call your transaction service)
            # For brevity, assuming transaction_operations is available
            from app.db.transaction_operations import TransactionOperations
            
            # Get different sets of transactions based on time period
            if time_period == "week":
                from datetime import timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                transactions = TransactionOperations.get_user_transactions_in_date_range(
                    user_id, start_date, end_date
                )
            elif time_period == "month":
                # Get current month transactions
                now = datetime.now()
                transactions = TransactionOperations.get_monthly_summary(
                    user_id, now.year, now.month
                )
            elif time_period == "quarter":
                # Get last 3 months of transactions
                from datetime import timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                transactions = TransactionOperations.get_user_transactions_in_date_range(
                    user_id, start_date, end_date
                )
            else:  # year
                # Get last 12 months of transactions
                from datetime import timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                transactions = TransactionOperations.get_user_transactions_in_date_range(
                    user_id, start_date, end_date
                )
            
            # Get sentiment analysis
            sentiment = await self.analyze_transaction_sentiment(transactions)
            
            # Get financial goals
            goals = user.get("financial_goals", [])
            
            # Generate insights using GenAI
            insights = await self.genai_service.generate_financial_insights(user, transactions)
            
            # Detect spending anomalies
            anomalies = await self.genai_service.detect_anomalies(transactions)
            
            # Predict upcoming expenses
            predicted_expenses = await self.genai_service.generate_predictive_expenses(transactions)
            
            # Compile the report
            report = {
                "user_id": user_id,
                "report_date": datetime.now(),
                "time_period": time_period,
                "sentiment": sentiment,
                "insights": insights,
                "anomalies": anomalies,
                "predicted_expenses": predicted_expenses,
                "goal_progress": self._calculate_goal_progress(goals),
                "summary": {
                    "financial_health": sentiment.get("financial_health", "stable"),
                    "key_insight": insights[0].get("description", "") if insights else "",
                    "upcoming_expenses": len(predicted_expenses),
                    "anomalies_detected": len(anomalies)
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating financial health report: {str(e)}")
            return {"error": f"Failed to generate report: {str(e)}"}
    
    async def _update_user_sentiment(self, user_id: str, sentiment_data: Dict[str, Any]) -> bool:
        """
        Update user profile with sentiment analysis
        
        Args:
            user_id: User ID
            sentiment_data: Sentiment analysis data
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Create sentiment data structure
            sentiment = {
                "overall_sentiment": sentiment_data.get("overall_sentiment", "neutral"),
                "confidence": sentiment_data.get("confidence", 0.5),
                "financial_health": sentiment_data.get("financial_health", "stable"),
                "explanation": sentiment_data.get("explanation", ""),
                "last_updated": datetime.now()
            }
            
            # Update user profile
            success = UserOperations.update_sentiment(user_id, sentiment)
            return success
        
        except Exception as e:
            logger.error(f"Error updating user sentiment: {str(e)}")
            return False
    
    def _calculate_goal_progress(self, goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate progress for each financial goal
        
        Args:
            goals: List of financial goals
            
        Returns:
            List of goal progress summaries
        """
        progress_summaries = []
        
        for goal in goals:
            # Calculate basic progress
            target_amount = goal.get("target_amount", 0)
            current_amount = goal.get("current_amount", 0)
            
            if target_amount <= 0:
                percentage = 0
            else:
                percentage = (current_amount / target_amount) * 100
            
            # Calculate time progress
            start_date = goal.get("created_at")
            target_date = goal.get("target_date")
            now = datetime.now()
            
            if not start_date or not target_date:
                time_progress = 0
            else:
                total_days = (target_date - start_date).days
                elapsed_days = (now - start_date).days
                
                if total_days <= 0:
                    time_progress = 100
                else:
                    time_progress = min(100, (elapsed_days / total_days) * 100)
            
            # Determine if on track
            on_track = percentage >= time_progress
            
            # Create summary
            summary = {
                "goal_id": goal.get("goal_id"),
                "name": goal.get("name"),
                "percentage": round(percentage, 1),
                "time_progress": round(time_progress, 1),
                "on_track": on_track,
                "target_amount": target_amount,
                "current_amount": current_amount,
                "monthly_contribution": goal.get("monthly_contribution", 0),
                "remaining": target_amount - current_amount
            }
            
            progress_summaries.append(summary)
        
        return progress_summaries