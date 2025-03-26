# seed_database.py
from app.db.connection import db
from datetime import datetime, timedelta
import uuid
import random
from app.db.user_operations import insert_dummy_users  # Corrected import
from app.db.transaction_operations import insert_dummy_transactions
from app.db.product_operations import insert_dummy_products
from app.db.recommendation_operations import insert_dummy_recommendations
from app.db.chat_operations import insert_dummy_chat_messages

# Collection reference
users_collection = db.users

def seed_database():
    """
    Seed the database with dummy data for all collections
    """
    print("Starting database seeding...")
    
    # Step 1: Create dummy users
    print("\nCreating dummy users...")
    user_ids = insert_dummy_users(4)
    
    # Step 2: Create dummy products
    print("\nCreating dummy products...")
    products = insert_dummy_products(7)
    
    # Step 3: Create dummy transactions
    print("\nCreating dummy transactions...")
    insert_dummy_transactions(user_ids, 40)
    
    # Step 4: Create dummy recommendations
    print("\nCreating dummy recommendations...")
    insert_dummy_recommendations(user_ids, products)
    
    # Step 5: Create dummy chat messages
    print("\nCreating dummy chat messages...")
    insert_dummy_chat_messages(user_ids, 8)
    
    print("\nDatabase seeding completed successfully!")

if __name__ == "__main__":
    seed_database()