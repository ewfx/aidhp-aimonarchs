from pymongo import ASCENDING, DESCENDING
from app.db.connection import db
from datetime import datetime, timedelta
import uuid
import random

# Collection reference
users_collection = db.users
recommendations_collection = db.recommendations

class RecommendationOperations:
    @staticmethod
    def create_recommendation(recommendation_data):
        """
        Create a new recommendation in the database
        
        Args:
            recommendation_data (dict): Recommendation data to insert
            
        Returns:
            str: ID of the created recommendation
        """
        # Add timestamp if not provided
        if "timestamp" not in recommendation_data:
            recommendation_data["timestamp"] = datetime.now()
        
        # Set expiration date if not provided
        if "expires_at" not in recommendation_data:
            recommendation_data["expires_at"] = datetime.now() + timedelta(days=30)
        
        # Generate recommendation_id if not provided
        if "recommendation_id" not in recommendation_data:
            recommendation_data["recommendation_id"] = str(uuid.uuid4())
        
        # Set default values for tracking fields
        if "is_viewed" not in recommendation_data:
            recommendation_data["is_viewed"] = False
        
        if "is_clicked" not in recommendation_data:
            recommendation_data["is_clicked"] = False
            
        result = recommendations_collection.insert_one(recommendation_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_recommendation_by_id(recommendation_id):
        """
        Get a recommendation by its ID
        
        Args:
            recommendation_id (str): Recommendation ID to search for
            
        Returns:
            dict: Recommendation document or None if not found
        """
        return recommendations_collection.find_one({"recommendation_id": recommendation_id})
    
    @staticmethod
    def get_user_recommendations(user_id, include_expired=False, limit=10):
        """
        Get recommendations for a specific user - NOT an async method
        
        Args:
            user_id (str): User ID to filter by
            include_expired (bool): Whether to include expired recommendations
            limit (int): Maximum number of recommendations to return
            
        Returns:
            list: List of recommendation documents
        """
        query = {"user_id": user_id}
        
        # Exclude expired recommendations if specified
        if not include_expired:
            query["expires_at"] = {"$gt": datetime.now()}
        
        # Get recommendations sorted by score (highest first)
        cursor = recommendations_collection.find(query).sort("score", DESCENDING).limit(limit)
        
        return list(cursor)

    @staticmethod
    def update_recommendation(recommendation_id, update_data):
        """
        Update a recommendation
        
        Args:
            recommendation_id (str): Recommendation ID to update
            update_data (dict): Data to update
            
        Returns:
            bool: True if update was successful
        """
        result = recommendations_collection.update_one(
            {"recommendation_id": recommendation_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def record_recommendation_feedback(recommendation_id, is_helpful, feedback_text=None):
        """
        Record user feedback on a recommendation
        
        Args:
            recommendation_id (str): Recommendation ID to update
            is_helpful (bool): Whether the recommendation was helpful
            feedback_text (str, optional): Additional feedback text
            
        Returns:
            bool: True if update was successful
        """
        update_data = {
            "feedback.is_helpful": is_helpful,
            "feedback.feedback_date": datetime.now()
        }
        
        if feedback_text:
            update_data["feedback.feedback_text"] = feedback_text
        
        result = recommendations_collection.update_one(
            {"recommendation_id": recommendation_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def record_recommendation_conversion(recommendation_id, is_converted):
        """
        Record whether a recommendation was converted (user took action)
        
        Args:
            recommendation_id (str): Recommendation ID to update
            is_converted (bool): Whether the recommendation was converted
            
        Returns:
            bool: True if update was successful
        """
        update_data = {
            "conversion.is_converted": is_converted,
            "conversion.conversion_date": datetime.now()
        }
        
        result = recommendations_collection.update_one(
            {"recommendation_id": recommendation_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_recommendation(recommendation_id):
        """
        Delete a recommendation
        
        Args:
            recommendation_id (str): Recommendation ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        result = recommendations_collection.delete_one({"recommendation_id": recommendation_id})
        return result.deleted_count > 0
    
    @staticmethod
    def mark_recommendation_viewed(recommendation_id):
        """
        Mark a recommendation as viewed
        
        Args:
            recommendation_id (str): Recommendation ID to update
            
        Returns:
            bool: True if update was successful
        """
        result = recommendations_collection.update_one(
            {"recommendation_id": recommendation_id},
            {"$set": {"is_viewed": True}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def mark_recommendation_clicked(recommendation_id):
        """
        Mark a recommendation as clicked
        
        Args:
            recommendation_id (str): Recommendation ID to update
            
        Returns:
            bool: True if update was successful
        """
        result = recommendations_collection.update_one(
            {"recommendation_id": recommendation_id},
            {"$set": {"is_clicked": True}}
        )
        
        return result.modified_count > 0


def insert_dummy_recommendations(user_ids, products=None, count_per_user=3):
    """
    Insert dummy recommendation data for specified users
    
    Args:
        user_ids (list): List of user IDs to create recommendations for
        products (list, optional): List of product documents
        count_per_user (int): Number of recommendations per user
        
    Returns:
        int: Number of recommendations created
    """
    total_created = 0
    
    # If no products provided, create some dummy products
    if not products:
        products = [
            {
                "product_id": "prod1",
                "name": "Premium Savings Account",
                "category": "Savings",
                "features": ["No minimum balance", "No monthly fees", "2.5% APY"]
            },
            {
                "product_id": "prod2",
                "name": "Growth Investment Fund",
                "category": "Investments",
                "features": ["Professionally managed", "Quarterly rebalancing", "12.3% average return"]
            },
            {
                "product_id": "prod3",
                "name": "Travel Rewards Credit Card",
                "category": "Credit Cards",
                "features": ["No foreign transaction fees", "50,000 bonus points", "Free travel insurance"]
            },
            {
                "product_id": "prod4",
                "name": "Home Mortgage",
                "category": "Loans",
                "features": ["Fixed rate", "15-30 year terms", "No prepayment penalties"]
            },
            {
                "product_id": "prod5",
                "name": "Retirement Plan",
                "category": "Retirement",
                "features": ["Tax advantages", "Employer matching", "Regular contributions"]
            }
        ]
    
    # Sample recommendation reasons
    reasons = {
        "Savings": [
            "Based on your consistent monthly deposits and moderate risk profile, this high-yield savings account would help you achieve your emergency fund goal faster with 2.5% APY.",
            "Your transaction history shows regular surplus cash that could earn more interest in this savings account."
        ],
        "Investments": [
            "Your financial data shows you have surplus income that could be invested for long-term growth. This fund is aligned with your moderate risk tolerance.",
            "Based on your risk profile and investment goals, this fund offers a good balance of growth potential and stability."
        ],
        "Credit Cards": [
            "Your transaction history shows frequent travel purchases. This card would earn you 3x points on travel and dining, maximizing rewards on your existing spending.",
            "Based on your spending patterns, you could earn over $500 in rewards annually with this card."
        ],
        "Loans": [
            "With current interest rates and your excellent credit score, refinancing your mortgage could save you $350 monthly.",
            "Based on your housing expenses and income, you may qualify for a mortgage with better terms than your current loan."
        ],
        "Retirement": [
            "You're currently on track to reach only 65% of your retirement goal. Increasing your contributions to this plan could help close the gap.",
            "Your retirement contributions are below recommended levels for your age and income. This plan offers tax advantages that could boost your savings."
        ]
    }
    
    for user_id in user_ids:
        # Randomly select products for this user (without replacement)
        user_products = random.sample(products, min(count_per_user, len(products)))
        
        for i, product in enumerate(user_products):
            # Generate a score (higher for first recommendations)
            score = random.randint(70, 95) - (i * 5)
            
            # Get category-specific reasons
            category_reasons = reasons.get(product["category"], ["This product matches your financial profile."])
            
            # Create recommendation
            recommendation = {
                "recommendation_id": str(uuid.uuid4()),
                "user_id": user_id,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "product_category": product["category"],
                "score": score,
                "reason": random.choice(category_reasons),
                "features": product.get("features", []),
                "timestamp": datetime.now() - timedelta(days=random.randint(0, 14)),
                "expires_at": datetime.now() + timedelta(days=random.randint(7, 30)),
                "is_viewed": random.random() < 0.7,  # 70% chance of being viewed
                "is_clicked": random.random() < 0.3,  # 30% chance of being clicked
                "feedback": {
                    "is_helpful": random.choice([True, False, None]),
                    "feedback_date": None
                },
                "conversion": {
                    "is_converted": random.random() < 0.1,  # 10% chance of conversion
                    "conversion_date": None
                }
            }
            
            # Set feedback date if feedback is provided
            if recommendation["feedback"]["is_helpful"] is not None:
                recommendation["feedback"]["feedback_date"] = recommendation["timestamp"] + timedelta(days=random.randint(1, 3))
            
            # Set conversion date if converted
            if recommendation["conversion"]["is_converted"]:
                recommendation["conversion"]["conversion_date"] = recommendation["timestamp"] + timedelta(days=random.randint(2, 7))
            
            # Insert the recommendation
            recommendations_collection.insert_one(recommendation)
            total_created += 1
    
    print(f"Created {total_created} dummy recommendations for {len(user_ids)} users")
    return total_created


if __name__ == "__main__":
    # Test the functions
    from user_operations import UserOperations
    from product_operations import ProductOperations, insert_dummy_products
    
    # Get some user IDs
    users = list(db.users.find({}, {"user_id": 1}).limit(3))
    user_ids = [user["user_id"] for user in users]
    
    if not user_ids:
        print("No users found. Creating some dummy users first...")
        from user_operations import insert_dummy_users
        user_ids = insert_dummy_users(3)
    
    # Get some products
    products = list(db.products.find({}))
    
    if not products:
        print("No products found. Creating some dummy products first...")
        products = insert_dummy_products(5)
    
    print("Inserting dummy recommendations...")
    insert_dummy_recommendations(user_ids, products)
    print("Done!")