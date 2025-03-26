from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import uuid
import asyncio

from app.db.user_operations import UserOperations
from app.db.transaction_operations import TransactionOperations
from app.services.genai_services import GenAIService

logger = logging.getLogger(__name__)

class InsightsService:
    """
    Service for generating personalized financial insights using GenAI
    """
    
    def __init__(self):
        """Initialize insights service with GenAI service"""
        self.genai_service = GenAIService()
    
    async def generate_user_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate insights for a user based on their financial data
        
        Args:
            user_id: User ID to generate insights for
            
        Returns:
            List of insight objects
        """
        try:
            # Get user profile
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return []
            
            # Get recent transactions
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = TransactionOperations.get_user_transactions_in_date_range(
                user_id, start_date, end_date
            )
            
            if not transactions:
                logger.info(f"No transaction data found for user {user_id}")
                return self._generate_fallback_insights(user)
            
            # Use GenAI to generate insights
            insights = await self.genai_service.generate_financial_insights(user, transactions)
            
            if not insights:
                logger.warning(f"No insights generated for user {user_id}")
                return self._generate_fallback_insights(user)
            
            # Process and enrich insights
            processed_insights = []
            
            for insight in insights:
                # Add insight ID and metadata
                processed_insight = {
                    "insight_id": f"ins{uuid.uuid4().hex[:8]}",
                    "category": insight.get("category", "general"),
                    "description": insight.get("description", ""),
                    "importance": insight.get("importance", "medium"),
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(days=30),
                    "is_read": False,
                    "is_acted_upon": None
                }
                
                processed_insights.append(processed_insight)
            
            # Update user profile with new insights
            if processed_insights:
                # Get existing insights
                existing_insights = user.get("insights", [])
                
                # Remove expired insights
                now = datetime.now()
                active_insights = [
                    insight for insight in existing_insights 
                    if "expires_at" not in insight or 
                    (isinstance(insight["expires_at"], datetime) and insight["expires_at"] > now)
                ]
                
                # Add new insights
                combined_insights = active_insights + processed_insights
                
                # Limit to 10 most recent insights
                if len(combined_insights) > 10:
                    combined_insights = sorted(
                        combined_insights, 
                        key=lambda x: x.get("created_at", datetime.now()), 
                        reverse=True
                    )[:10]
                
                # Update user profile
                UserOperations.update_user(user_id, {"insights": combined_insights})
            
            return processed_insights
            
        except Exception as e:
            logger.error(f"Error generating insights for user {user_id}: {str(e)}")
            return self._generate_fallback_insights(user)
    
    def _generate_fallback_insights(self, user: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate fallback insights when GenAI fails or no data is available
        
        Args:
            user: User profile data (optional)
            
        Returns:
            List of basic insight objects
        """
        now = datetime.now()
        
        # Create basic fallback insights
        insights = [
            {
                "insight_id": f"ins{uuid.uuid4().hex[:8]}",
                "category": "general",
                "description": "Tracking your expenses regularly can help you identify spending patterns and opportunities to save.",
                "importance": "medium",
                "created_at": now,
                "expires_at": now + timedelta(days=30),
                "is_read": False,
                "is_acted_upon": None
            }
        ]
        
        # Add insights based on user profile if available
        if user:
            financial_profile = user.get("financial_profile", {})
            financial_goals = user.get("financial_goals", [])
            
            # Check for emergency fund
            has_emergency_fund = any(goal.get("type") == "emergency_fund" for goal in financial_goals)
            
            if not has_emergency_fund:
                insights.append({
                    "insight_id": f"ins{uuid.uuid4().hex[:8]}",
                    "category": "savings",
                    "description": "Having an emergency fund covering 3-6 months of expenses is essential for financial security.",
                    "importance": "high",
                    "created_at": now,
                    "expires_at": now + timedelta(days=30),
                    "is_read": False,
                    "is_acted_upon": None
                })
            
            # Check debt levels
            debt = financial_profile.get("debt", 0)
            income = financial_profile.get("monthly_income", 0) * 12  # Annual income
            
            if debt > 0 and income > 0 and debt > income * 0.5:
                insights.append({
                    "insight_id": f"ins{uuid.uuid4().hex[:8]}",
                    "category": "debt",
                    "description": "Your debt-to-income ratio is high. Focusing on debt reduction can improve your financial health.",
                    "importance": "high",
                    "created_at": now,
                    "expires_at": now + timedelta(days=30),
                    "is_read": False,
                    "is_acted_upon": None
                })
        
        return insights
    
    async def refresh_all_user_insights(self) -> Dict[str, Any]:
        """
        Background job to refresh insights for all users
        
        Returns:
            Dict with job statistics
        """
        try:
            # Get all active users
            # This would typically be paginated in a real system
            users = list(UserOperations._get_all_users())
            
            processed_count = 0
            success_count = 0
            error_count = 0
            
            for user in users:
                try:
                    user_id = user.get("user_id")
                    if not user_id:
                        continue
                    
                    processed_count += 1
                    
                    # Generate insights for this user
                    insights = await self.generate_user_insights(user_id)
                    
                    if insights:
                        success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error refreshing insights for user {user.get('user_id')}: {str(e)}")
                    
                # Add a small delay to avoid overloading the system
                await asyncio.sleep(0.1)
            
            return {
                "job_id": f"insights_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_time": datetime.now().isoformat(),
                "users_processed": processed_count,
                "success_count": success_count,
                "error_count": error_count
            }
            
        except Exception as e:
            logger.error(f"Error in refresh_all_user_insights: {str(e)}")
            return {
                "error": f"Failed to refresh insights: {str(e)}",
                "job_id": f"insights_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_time": datetime.now().isoformat()
            }
    
    def mark_insight_read(self, user_id: str, insight_id: str) -> bool:
        """
        Mark an insight as read
        
        Args:
            user_id: User ID
            insight_id: Insight ID to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user profile
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                return False
            
            # Get insights
            insights = user.get("insights", [])
            
            # Find the specific insight
            updated = False
            for insight in insights:
                if insight.get("insight_id") == insight_id:
                    insight["is_read"] = True
                    updated = True
                    break
            
            if updated:
                # Update user profile
                success = UserOperations.update_user(user_id, {"insights": insights})
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking insight as read: {str(e)}")
            return False
    
    def record_insight_action(self, user_id: str, insight_id: str, acted_upon: bool) -> bool:
        """
        Record whether a user acted upon an insight
        
        Args:
            user_id: User ID
            insight_id: Insight ID
            acted_upon: Whether the user acted upon the insight
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user profile
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                return False
            
            # Get insights
            insights = user.get("insights", [])
            
            # Find the specific insight
            updated = False
            for insight in insights:
                if insight.get("insight_id") == insight_id:
                    insight["is_acted_upon"] = acted_upon
                    updated = True
                    break
            
            if updated:
                # Update user profile
                success = UserOperations.update_user(user_id, {"insights": insights})
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error recording insight action: {str(e)}")
            return False
    
    async def generate_insights_from_transaction(self, user_id: str, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights based on a specific new transaction
        
        Args:
            user_id: User ID
            transaction: Transaction data
            
        Returns:
            List of insight objects related to the transaction
        """
        try:
            # This would typically use a specialized GenAI method for transaction insights
            # For now, we'll implement a simple rule-based system
            
            insights = []
            amount = transaction.get("amount", 0)
            category = transaction.get("category", "")
            merchant = transaction.get("merchant", "")
            
            # Skip income transactions
            if amount >= 0:
                return []
            
            # Get user profile
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                return []
            
            financial_profile = user.get("financial_profile", {})
            
            # Insight 1: Large transaction
            monthly_income = financial_profile.get("monthly_income", 0)
            if monthly_income > 0 and abs(amount) > monthly_income * 0.2:
                insights.append({
                    "insight_id": f"ins{uuid.uuid4().hex[:8]}",
                    "category": "spending",
                    "description": f"Your recent {category} expense of ${abs(amount):.2f} was more than 20% of your monthly income.",
                    "importance": "high",
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(days=7),
                    "is_read": False,
                    "is_acted_upon": None,
                    "related_transaction_id": transaction.get("transaction_id")
                })
            
            # Insight 2: Subscription detection
            if "subscription" in category.lower() or any(sub in merchant.lower() for sub in ["netflix", "spotify", "hulu", "disney", "apple", "amazon prime"]):
                insights.append({
                    "insight_id": f"ins{uuid.uuid4().hex[:8]}",
                    "category": "subscription",
                    "description": f"We detected a subscription payment to {merchant}. Regularly reviewing your subscriptions can help optimize your spending.",
                    "importance": "medium",
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(days=30),
                    "is_read": False,
                    "is_acted_upon": None,
                    "related_transaction_id": transaction.get("transaction_id")
                })
            
            # Insight 3: Category-specific insights
            if category.lower() == "dining" and abs(amount) > 100:
                insights.append({
                    "insight_id": f"ins{uuid.uuid4().hex[:8]}",
                    "category": "dining",
                    "description": f"Your dining expense of ${abs(amount):.2f} at {merchant} was on the higher side. Consider setting a dining budget to track these expenses.",
                    "importance": "low",
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(days=14),
                    "is_read": False,
                    "is_acted_upon": None,
                    "related_transaction_id": transaction.get("transaction_id")
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights from transaction: {str(e)}")
            return []