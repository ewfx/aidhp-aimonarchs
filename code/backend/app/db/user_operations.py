# app/db/user_operations.py
from app.db.connection import db
from datetime import datetime, timedelta
import uuid
import random
from uuid import UUID


# Collection reference
users_collection = db.users

class UserOperations:
    @staticmethod
    def create_user(user_data):
        """
        Create a new user in the database
        
        Args:
            user_data (dict): User data to insert
            
        Returns:
            str: ID of the created user
        """
        # Add created_at and updated_at timestamps
        user_data["created_at"] = datetime.now()
        user_data["updated_at"] = datetime.now()
        
        # Generate user_id if not provided
        if "user_id" not in user_data:
            user_data["user_id"] = str(uuid.uuid4())
            
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_by_id(user_id: str):
  
        try:
            # Attempt to convert to UUID if needed
            user_id_uuid = UUID(user_id)
            # You could use user_id_uuid in the query if needed
        except (ValueError, TypeError):
            # Continue with original ID if not a valid UUID
            pass
        
        return users_collection.find_one({"user_id": user_id})

    @staticmethod
    def get_user_by_email(email):
        """
        Get a user by their email
        
        Args:
            email (str): Email to search for
            
        Returns:
            dict: User document or None if not found
        """
        return users_collection.find_one({"email": email})
    
    @staticmethod
    def update_user(user_id, update_data):
        """
        Update a user's information
        
        Args:
            user_id (str): User ID to update
            update_data (dict): Data to update
            
        Returns:
            bool: True if update was successful
        """
        # Update the updated_at timestamp
        update_data["updated_at"] = datetime.now()
        
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_user(user_id):
        """
        Delete a user from the database
        
        Args:
            user_id (str): User ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        result = users_collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0
    
    @staticmethod
    def add_financial_goal(user_id, goal_data):
        """
        Add a new financial goal to a user
        
        Args:
            user_id (str): User ID to update
            goal_data (dict): Goal data to add
            
        Returns:
            bool: True if addition was successful
        """
        # Add goal_id and created_at if not provided
        if "goal_id" not in goal_data:
            goal_data["goal_id"] = str(uuid.uuid4())
        
        if "created_at" not in goal_data:
            goal_data["created_at"] = datetime.now()
        
        result = users_collection.update_one(
            {"user_id": user_id},
            {
                "$push": {"financial_goals": goal_data},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def update_financial_goal(user_id, goal_id, update_data):
        """
        Update a financial goal
        
        Args:
            user_id (str): User ID
            goal_id (str): Goal ID to update
            update_data (dict): Data to update
            
        Returns:
            bool: True if update was successful
        """
        # Prefix each key with financial_goals.$
        prefixed_update = {f"financial_goals.$.{k}": v for k, v in update_data.items()}
        
        result = users_collection.update_one(
            {"user_id": user_id, "financial_goals.goal_id": goal_id},
            {
                "$set": prefixed_update,
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def add_insight(user_id, insight_data):
        """
        Add a new AI insight to a user
        
        Args:
            user_id (str): User ID to update
            insight_data (dict): Insight data to add
            
        Returns:
            bool: True if addition was successful
        """
        # Add insight_id and created_at if not provided
        if "insight_id" not in insight_data:
            insight_data["insight_id"] = str(uuid.uuid4())
        
        if "created_at" not in insight_data:
            insight_data["created_at"] = datetime.now()
        
        # Set default expiration to 30 days if not provided
        if "expires_at" not in insight_data:
            insight_data["expires_at"] = datetime.now() + timedelta(days=30)
        
        result = users_collection.update_one(
            {"user_id": user_id},
            {
                "$push": {"insights": insight_data},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def update_sentiment(user_id, sentiment_data):
        """
        Update a user's sentiment analysis
        
        Args:
            user_id (str): User ID to update
            sentiment_data (dict): Sentiment data to update
            
        Returns:
            bool: True if update was successful
        """
        # Add current sentiment to history
        current_sentiment = {
            "date": datetime.now(),
            "sentiment": sentiment_data.get("overall_sentiment", "neutral").lower(),
            "confidence": sentiment_data.get("confidence", 0.5)
        }
        
        sentiment_data["last_updated"] = datetime.now()
        
        result = users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {"sentiment": sentiment_data, "updated_at": datetime.now()},
                "$push": {"sentiment.history": current_sentiment}
            }
        )
        
        return result.modified_count > 0


def insert_dummy_users(count=3):
    """
    Insert dummy user data into the database
    
    Args:
        count (int): Number of dummy users to create
        
    Returns:
        list: List of created user IDs
    """
    dummy_users = []
    
    # Sample data for variation
    names = ["John Doe", "Jane Smith", "Michael Johnson", "Emily Wilson", "David Brown"]
    occupations = ["Software Engineer", "Financial Analyst", "Doctor", "Teacher", "Marketing Manager"]
    income_brackets = ["low", "middle", "high", "very_high"]
    risk_profiles = ["Conservative", "Moderate", "Aggressive"]
    financial_health = ["Excellent", "Good", "Fair", "Needs Attention"]
    goal_types = ["retirement", "home_purchase", "education", "emergency_fund", "vacation", "car_purchase"]
    
    for i in range(count):
        # Generate unique user_id and email
        user_id = str(uuid.uuid4())
        name = random.choice(names)
        email = f"{name.lower().replace(' ', '.')}_{i}@example.com"
        
        # Create user object
        user = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "phone": f"+1{random.randint(1000000000, 9999999999)}",
            "created_at": datetime.now() - timedelta(days=random.randint(10, 365)),
            "updated_at": datetime.now(),
            "last_login": datetime.now() - timedelta(days=random.randint(0, 10)),
            
            "profile": {
                "age": random.randint(25, 65),
                "occupation": random.choice(occupations),
                "income_bracket": random.choice(income_brackets),
                "marital_status": random.choice(["single", "married", "divorced"]),
                "dependents": random.randint(0, 3),
                "education": random.choice(["high_school", "bachelors", "masters", "phd"]),
                "location": {
                    "city": random.choice(["New York", "San Francisco", "Chicago", "Austin"]),
                    "state": random.choice(["NY", "CA", "IL", "TX"]),
                    "country": "USA",
                    "zip": f"{random.randint(10000, 99999)}"
                }
            },
            
            "financial_profile": {
                "account_number": f"****{random.randint(1000, 9999)}",
                "balance": round(random.uniform(5000, 50000), 2),
                "savings": round(random.uniform(10000, 100000), 2),
                "investments": round(random.uniform(0, 200000), 2),
                "debt": round(random.uniform(0, 150000), 2),
                "credit_score": random.randint(580, 850),
                "risk_profile": random.choice(risk_profiles),
                "financial_health": random.choice(financial_health),
                "monthly_income": round(random.uniform(4000, 15000), 2),
                "monthly_expenses": round(random.uniform(2000, 8000), 2),
                "last_assessment_date": datetime.now() - timedelta(days=random.randint(0, 30))
            },
            
            "financial_goals": [],
            
            "preferences": {
                "preferred_categories": random.sample(["investments", "savings", "retirement", "credit", "insurance"], k=random.randint(1, 3)),
                "notification_settings": {
                    "email": random.choice([True, False]),
                    "push": random.choice([True, False]),
                    "sms": random.choice([True, False])
                },
                "dashboard_widgets": random.sample(["balance", "spending", "goals", "recommendations"], k=random.randint(2, 4)),
                "theme": random.choice(["light", "dark", "system"])
            },
            
            "sentiment": {
                "overall_sentiment": random.choice(["Positive", "Neutral", "Negative"]),
                "confidence": round(random.uniform(0.5, 0.95), 2),
                "financial_health": random.choice(["excellent", "good", "fair", "stressed"]).lower(),
                "last_updated": datetime.now() - timedelta(days=random.randint(0, 7)),
                "history": []
            },
            
            "insights": [],
            "anomalies": [],
            "predicted_expenses": []
        }
        
        # Add 1-3 financial goals
        for j in range(random.randint(1, 3)):
            goal_type = random.choice(goal_types)
            target_amount = round(random.uniform(10000, 500000), 2)
            current_amount = round(random.uniform(0, target_amount * 0.7), 2)
            
            goal = {
                "goal_id": f"goal{j+1}_{user_id[:8]}",
                "type": goal_type,
                "name": f"{goal_type.replace('_', ' ').title()} Fund",
                "target_amount": target_amount,
                "current_amount": current_amount,
                "target_date": datetime.now() + timedelta(days=random.randint(365, 3650)),
                "monthly_contribution": round(random.uniform(200, 2000), 2),
                "priority": random.choice(["low", "medium", "high"]),
                "created_at": datetime.now() - timedelta(days=random.randint(10, 300))
            }
            
            user["financial_goals"].append(goal)
        
        # Add 1-2 insights
        insights = [
            "Based on your spending patterns, you could save $320 monthly by reducing restaurant expenses.",
            "You're on track to reach your emergency fund goal by September 2025.",
            "Your investment portfolio is underperforming the market by 2.3%. Consider rebalancing.",
            "You've paid $230 in avoidable fees in the last 3 months."
        ]
        
        for j in range(random.randint(1, 2)):
            insight = {
                "insight_id": f"ins{j+1}_{user_id[:8]}",
                "category": random.choice(["spending", "savings", "investment", "fees"]),
                "description": random.choice(insights),
                "created_at": datetime.now() - timedelta(days=random.randint(0, 30)),
                "expires_at": datetime.now() + timedelta(days=random.randint(1, 30)),
                "is_read": random.choice([True, False]),
                "is_acted_upon": random.choice([True, False, None])
            }
            
            user["insights"].append(insight)
        
        # Add 0-1 anomalies
        if random.choice([True, False]):
            anomaly = {
                "anomaly_id": f"ano1_{user_id[:8]}",
                "category": random.choice(["Entertainment", "Dining", "Shopping", "Travel"]),
                "description": f"{random.randint(30, 80)}% increase from average",
                "amount": round(random.uniform(100, 500), 2),
                "detection_date": datetime.now() - timedelta(days=random.randint(0, 7)),
                "is_acknowledged": random.choice([True, False])
            }
            
            user["anomalies"].append(anomaly)
        
        # Add 2-3 predicted expenses
        expense_descriptions = ["Rent payment", "Car insurance", "Student loan", "Credit card payment", "Utility bill"]
        
        for j in range(random.randint(2, 3)):
            expense = {
                "expense_id": f"exp{j+1}_{user_id[:8]}",
                "description": expense_descriptions[j % len(expense_descriptions)],
                "amount": round(random.uniform(100, 2000), 2),
                "due_date": datetime.now() + timedelta(days=random.randint(1, 30)),
                "category": random.choice(["Housing", "Insurance", "Loan", "Utilities"]),
                "confidence": round(random.uniform(0.8, 0.99), 2),
                "is_recurring": random.choice([True, False])
            }
            
            user["predicted_expenses"].append(expense)
        
        # Add sentiment history (2-3 entries)
        for j in range(random.randint(2, 3)):
            history_entry = {
                "date": datetime.now() - timedelta(days=j*30),
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "confidence": round(random.uniform(0.5, 0.95), 2)
            }
            
            user["sentiment"]["history"].append(history_entry)
        
        # Insert the user
        users_collection.insert_one(user)
        dummy_users.append(user_id)
    
    print(f"Created {count} dummy users")
    return dummy_users


if __name__ == "__main__":
    # Test the functions
    print("Inserting dummy users...")
    insert_dummy_users(3)
    print("Done!")