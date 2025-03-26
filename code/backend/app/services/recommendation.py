from app.utils.database import users, transactions, products, recommendations
import random
from datetime import datetime
import uuid
from app.utils.mongo_utils import serialize_mongo_doc

class RecommendationService:
    @staticmethod
    async def generate_recommendations(user_id: str, count: int = 3):
        """
        Generate product recommendations for a user
        
        This is an async method that should be awaited
        """
        # Get user profile
        user = users.find_one({"user_id": user_id})
        if not user:
            return []
        
        # Serialize MongoDB document
        user = serialize_mongo_doc(user)
        
        # Get all products
        all_products = list(products.find())
        if not all_products:
            return []
        
        # Serialize MongoDB documents
        all_products = serialize_mongo_doc(all_products)
        
        # Filter products based on user profile
        suitable_products = []
        
        for product in all_products:
            # Simple matching based on income and risk profile
            if (not product.get("min_income") or user.get("income_bracket") in ["high", "very_high"]) and \
               (not product.get("risk_level") or product.get("risk_level") == user.get("risk_profile")):
                suitable_products.append(product)
        
        # If we don't have enough suitable products, add some random ones
        if len(suitable_products) < count:
            # Get random products from remaining products
            remaining_products = [p for p in all_products if p not in suitable_products]
            if remaining_products:
                additional_needed = min(count - len(suitable_products), len(remaining_products))
                random_additional = random.sample(remaining_products, additional_needed)
                suitable_products.extend(random_additional)
        
        # In case we have more suitable products than requested, randomly select
        if len(suitable_products) > count:
            suitable_products = random.sample(suitable_products, count)
        
        # Generate recommendation records
        recommendation_records = []
        
        for product in suitable_products:
            # Calculate a mock recommendation score
            score = round(random.uniform(0.7, 1.0) * 100, 0)
            
            # Create a simple reason
            reason = f"Based on your {user.get('risk_profile', 'moderate')} risk profile and financial goals."
            
            # Create recommendation record
            recommendation = {
                "recommendation_id": str(uuid.uuid4()),
                "user_id": user_id,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "product_category": product["category"],
                "score": score,
                "reason": reason,
                "timestamp": datetime.now(),
                "is_viewed": False,
                "is_clicked": False,
                "features": product.get("features", [])
            }
            
            # Save to database
            result = recommendations.insert_one(recommendation)
            
            # Serialize and add to return list
            serialized_recommendation = serialize_mongo_doc(recommendation)
            recommendation_records.append(serialized_recommendation)
        
        return recommendation_records