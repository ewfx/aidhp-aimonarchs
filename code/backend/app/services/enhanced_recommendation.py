from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Any
import logging

from app.db.user_operations import UserOperations
from app.db.transaction_operations import TransactionOperations
from app.db.product_operations import ProductOperations
from app.db.recommendation_operations import RecommendationOperations
from app.services.genai_services import GenAIService

logger = logging.getLogger(__name__)

class EnhancedRecommendationService:
    """
    Enhanced recommendation service that uses GenAI to generate personalized recommendations
    """
    
    def __init__(self):
        """Initialize the recommendation service with GenAI service"""
        self.genai_service = GenAIService()
    
    async def generate_recommendations(self, user_id: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate product recommendations for a user using GenAI
        
        Args:
            user_id: The user ID to generate recommendations for
            count: Number of recommendations to generate
            
        Returns:
            List of recommendation objects
        """
        try:
            # Get user profile
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return []
            
            # Get transaction history for context
            transactions = TransactionOperations.get_user_transactions(
                user_id=user_id, 
                limit=100,  # Get more transactions for better context
                sort_by="timestamp",
                sort_order=-1
            )
            
            # Get all products
            all_products = ProductOperations.get_products(active_only=True)
            if not all_products:
                logger.warning("No products found in database")
                return []
            
            # Pre-filter products based on basic eligibility
            # This reduces the number of GenAI calls needed
            eligible_products = ProductOperations.get_products_by_eligibility(
                income=user.get('financial_profile', {}).get('monthly_income'),
                credit_score=user.get('financial_profile', {}).get('credit_score'),
                risk_level=user.get('financial_profile', {}).get('risk_profile'),
                age=user.get('profile', {}).get('age')
            )
            
            if not eligible_products:
                # If no eligible products found, use all products
                eligible_products = all_products
                logger.info(f"No eligible products found, using all {len(all_products)} products")
            else:
                logger.info(f"Found {len(eligible_products)} eligible products out of {len(all_products)} total")
            
            # If we still have more eligible products than requested,
            # do a basic pre-ranking based on simple rules
            if len(eligible_products) > count:
                # Sort by eligibility matching (more matching criteria = higher rank)
                eligible_products = sorted(eligible_products, 
                    key=lambda p: self._basic_eligibility_score(p, user),
                    reverse=True
                )
            
            # Generate detailed recommendations with GenAI
            # starting with the highest ranked products from pre-filtering
            recommendation_records = []
            processed_products = 0
            max_products_to_try = min(count * 2, len(eligible_products))
            
            for product in eligible_products[:max_products_to_try]:
                if len(recommendation_records) >= count:
                    break
                
                processed_products += 1
                
                try:
                    # Generate personalized recommendation using GenAI
                    recommendation_data = await self.genai_service.generate_product_recommendation(
                        user_profile=user,
                        product=product,
                        transaction_history=transactions
                    )
                    # print(recommendation_data)
                    
                    # Extract data from the GenAI response
                    recommendation_text = recommendation_data.get("recommendation_text", "")
                    score = recommendation_data.get("score", 75)
                    
                    # Only include recommendations above a certain score threshold
                    if score < 60:
                        logger.info(f"Skipping product {product['product_id']} with low score {score}")
                        continue
                    
                    # Create recommendation record
                    recommendation = {
                        "recommendation_id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "product_id": product["product_id"],
                        "product_name": product["name"],
                        "product_category": product["category"],
                        "score": score,
                        "reason": recommendation_text,
                        "timestamp": datetime.now(),
                        "expires_at": datetime.now() + timedelta(days=30),
                        "is_viewed": False,
                        "is_clicked": False,
                        "features": product.get("features", []),
                        "metadata": {
                            "genai_generated": True,
                            "generation_time": datetime.now().isoformat()
                        },
                        "feedback": {
                            "is_helpful": None,
                            "feedback_date": None
                        },
                        "conversion": {
                            "is_converted": False,
                            "conversion_date": None
                        }
                    }
                    
                    # Save to database using recommendation operations
                    rec_id = RecommendationOperations.create_recommendation(recommendation)
                    recommendation["_id"] = str(recommendation.pop("_id"))
                    # print(type(recommendation["_id"]))
                    # Add to return list
                    recommendation_records.append(recommendation)
                    
                except Exception as e:
                    logger.error(f"Error generating recommendation for product {product['product_id']}: {str(e)}")
                    continue
            
            print(f"Generated {len(recommendation_records)} recommendations for user {user_id} from {processed_products} products")
            return recommendation_records
            
        except Exception as e:
            logger.error(f"Error in recommendation generation for user {user_id}: {str(e)}")
            return []
    
    def _basic_eligibility_score(self, product: Dict[str, Any], user: Dict[str, Any]) -> int:
        """
        Calculate a basic eligibility score based on matching criteria
        
        Args:
            product: Product data
            user: User profile data
            
        Returns:
            Score (higher is better)
        """
        score = 0
        
        # Extract user data with safe defaults
        financial_profile = user.get('financial_profile', {})
        profile = user.get('profile', {})
        
        income = financial_profile.get('monthly_income', 0)
        credit_score = financial_profile.get('credit_score', 0)
        risk_level = financial_profile.get('risk_profile', '').lower()
        age = profile.get('age', 0)
        
        # Extract product eligibility criteria
        eligibility = product.get('eligibility', {})
        min_income = eligibility.get('min_income', 0)
        min_credit_score = eligibility.get('min_credit_score', 0)
        product_risk_level = eligibility.get('risk_level', '').lower()
        target_age_min = eligibility.get('target_age_min', 0)
        target_age_max = eligibility.get('target_age_max', 999)
        
        # Check income match
        if min_income > 0 and income >= min_income:
            score += 1
        
        # Check credit score match
        if min_credit_score > 0 and credit_score >= min_credit_score:
            score += 1
        
        # Check risk level match
        if product_risk_level and risk_level == product_risk_level:
            score += 2  # Higher weight for risk match
        
        # Check age range match
        if age >= target_age_min and age <= target_age_max:
            score += 1
            
        # Adjust score based on product category matching user preferences
        if product.get('category', '') in user.get('preferences', {}).get('preferred_categories', []):
            score += 3  # Significant boost for preferred categories
            
        # Check if product matches any user financial goals
        product_category = product.get('category', '').lower()
        for goal in user.get('financial_goals', []):
            goal_type = goal.get('type', '').lower()
            
            if (product_category == 'savings' and goal_type in ['emergency_fund', 'savings']) or \
               (product_category == 'investments' and goal_type in ['retirement', 'investment']) or \
               (product_category == 'loans' and goal_type in ['home_purchase', 'car_purchase']):
                score += 2
                break
        
        return score
            
    async def refresh_recommendation_content(self, recommendation_id: str) -> bool:
        """
        Refresh the content of an existing recommendation using GenAI
        
        Args:
            recommendation_id: The recommendation ID to refresh
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the existing recommendation
            recommendation = RecommendationOperations.get_recommendation_by_id(recommendation_id)
            if not recommendation:
                logger.warning(f"Recommendation not found: {recommendation_id}")
                return False
            
            # Get user and product data
            user_id = recommendation.get("user_id")
            product_id = recommendation.get("product_id")
            
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False
                
            product = ProductOperations.get_product_by_id(product_id)
            if not product:
                logger.warning(f"Product not found: {product_id}")
                return False
            
            # Get transaction history for context
            transactions = TransactionOperations.get_user_transactions(
                user_id=user_id, 
                limit=50,
                sort_by="timestamp",
                sort_order=-1
            )
            
            # Generate new recommendation content
            recommendation_data = await self.genai_service.generate_product_recommendation(
                user_profile=user,
                product=product,
                transaction_history=transactions
            )
            
            # Extract data from the GenAI response
            recommendation_text = recommendation_data.get("recommendation_text", "")
            score = recommendation_data.get("score", recommendation.get("score", 75))
            
            # Update the recommendation
            update_data = {
                "reason": recommendation_text,
                "score": score,
                "updated_at": datetime.now(),
                "metadata": {
                    "genai_generated": True,
                    "generation_time": datetime.now().isoformat(),
                    "is_refresh": True
                }
            }
            
            success = RecommendationOperations.update_recommendation(recommendation_id, update_data)
            return success
            
        except Exception as e:
            logger.error(f"Error refreshing recommendation {recommendation_id}: {str(e)}")
            return False
            
    async def generate_comparison(self, recommendation_ids: List[str]) -> Dict[str, Any]:
        """
        Generate a comparison between multiple recommendations
        
        Args:
            recommendation_ids: List of recommendation IDs to compare
            
        Returns:
            Dict with comparison information
        """
        try:
            if not recommendation_ids or len(recommendation_ids) < 2:
                return {"error": "At least two recommendations are required for comparison"}
                
            recommendations = []
            user_id = None
            
            # Get all recommendation data
            for rec_id in recommendation_ids:
                rec = RecommendationOperations.get_recommendation_by_id(rec_id)
                if not rec:
                    logger.warning(f"Recommendation not found: {rec_id}")
                    continue
                    
                # Make sure all recommendations are for the same user
                if user_id is None:
                    user_id = rec.get("user_id")
                elif user_id != rec.get("user_id"):
                    return {"error": "All recommendations must be for the same user"}
                    
                # Get product details
                product = ProductOperations.get_product_by_id(rec.get("product_id"))
                if not product:
                    logger.warning(f"Product not found: {rec.get('product_id')}")
                    continue
                    
                # Combine recommendation and product data
                combined_data = {
                    "recommendation_id": rec.get("recommendation_id"),
                    "product_id": rec.get("product_id"),
                    "product_name": rec.get("product_name"),
                    "product_category": rec.get("product_category"),
                    "score": rec.get("score"),
                    "features": rec.get("features", []),
                    "description": product.get("description", ""),
                    "details": product.get("details", {})
                }
                
                recommendations.append(combined_data)
                
            if len(recommendations) < 2:
                return {"error": "Could not find enough valid recommendations for comparison"}
                
            # Get user profile for context
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                return {"error": "User not found"}
                
            # Generate comparison using GenAI
            # This would typically call a method in GenAIService, but for simplicity
            # we'll just create a mock response here
            
            comparison = {
                "recommendations": recommendations,
                "comparison_points": [
                    {
                        "name": "Interest Rate",
                        "description": "Annual interest rate or yield",
                        "values": {rec["recommendation_id"]: rec.get("details", {}).get("interest_rate", "N/A") for rec in recommendations}
                    },
                    {
                        "name": "Fees",
                        "description": "Monthly or annual fees",
                        "values": {rec["recommendation_id"]: rec.get("details", {}).get("monthly_fee", "N/A") for rec in recommendations}
                    },
                    {
                        "name": "Risk Level",
                        "description": "Investment risk level",
                        "values": {rec["recommendation_id"]: rec.get("details", {}).get("risk_level", "N/A") for rec in recommendations}
                    }
                ],
                "recommendation": "Based on your financial profile and goals, Product A offers better long-term value despite higher fees, while Product B provides more flexibility with lower initial returns."
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error generating comparison: {str(e)}")
            return {"error": f"Failed to generate comparison: {str(e)}"}