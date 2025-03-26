# app/db/user_operations.py
from app.db.connection import db
from datetime import datetime, timedelta
import uuid
import random

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
    
    # Rest of the class methods remain the same
    # ...

def insert_dummy_users(count=3):
    """
    Insert dummy user data into the database
    
    Args:
        count (int): Number of dummy users to create
        
    Returns:
        list: List of created user IDs
    """
    # Implementation remains the same
    # ...


if __name__ == "__main__":
    # Test the functions
    print("Inserting dummy users...")
    insert_dummy_users(3)
    print("Done!")