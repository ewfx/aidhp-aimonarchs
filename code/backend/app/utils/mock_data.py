import uuid
from datetime import datetime, timedelta
import random
from app.utils.database import users, transactions, products, recommendations

# Sample banking products
sample_products = [
    {
        "product_id": str(uuid.uuid4()),
        "name": "Premium Savings Account",
        "category": "savings",
        "description": "High-interest savings account for high-income customers",
        "features": ["High interest rate", "No monthly fees", "Free international transfers"],
        "min_income": 100000,
        "risk_level": "conservative",
        "target_age_min": 25,
        "target_age_max": 65
    },
    {
        "product_id": str(uuid.uuid4()),
        "name": "Student Checking Account",
        "category": "checking",
        "description": "No-fee checking account for students",
        "features": ["No minimum balance", "No monthly fees", "Free debit card"],
        "min_income": 0,
        "risk_level": "conservative",
        "target_age_min": 18,
        "target_age_max": 25
    },
    {
        "product_id": str(uuid.uuid4()),
        "name": "Growth Investment Fund",
        "category": "investments",
        "description": "High-growth investment fund for aggressive investors",
        "features": ["High returns", "Professionally managed", "Quarterly rebalancing"],
        "min_income": 75000,
        "risk_level": "aggressive",
        "target_age_min": 25,
        "target_age_max": 45
    },
    {
        "product_id": str(uuid.uuid4()),
        "name": "Retirement Planner",
        "category": "retirement",
        "description": "Long-term retirement planning with moderate risk",
        "features": ["Tax advantages", "Employer matching", "Regular contributions"],
        "min_income": 50000,
        "risk_level": "moderate",
        "target_age_min": 30,
        "target_age_max": 55
    },
    {
        "product_id": str(uuid.uuid4()),
        "name": "Home Mortgage",
        "category": "loans",
        "description": "Fixed-rate home mortgage with competitive rates",
        "features": ["Fixed rate", "15-30 year terms", "No prepayment penalties"],
        "min_income": 60000,
        "risk_level": "moderate",
        "target_age_min": 25,
        "target_age_max": 65
    }
]

# Sample user profiles
sample_users = [
    {
        "user_id": str(uuid.uuid4()),
        "email": "john.doe@example.com",
        "name": "John Doe",
        "age": 35,
        "income_bracket": "high",
        "balance": 1234678.0,
        "risk_profile": "aggressive",
        "financial_goals": ["home_purchase", "retirement"],
        "preferred_categories": ["loans", "investments"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "user_id": str(uuid.uuid4()),
        "email": "jane.smith@example.com",
        "name": "Jane Smith",
        "age": 22,
        "income_bracket": "low",
        "balance": 1234.0,
        "risk_profile": "conservative",
        "financial_goals": ["education", "savings"],
        "preferred_categories": ["checking", "savings"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "user_id": str(uuid.uuid4()),
        "email": "mike.wilson@example.com",
        "name": "Mike Wilson",
        "age": 45,
        "income_bracket": "very_high",
        "balance": 12345566778899.0,
        "risk_profile": "moderate",
        "financial_goals": ["retirement", "education"],
        "preferred_categories": ["investments", "retirement"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
]

# Transaction categories
transaction_categories = [
    "groceries", "dining", "entertainment", "utilities", 
    "rent", "mortgage", "transportation", "shopping", 
    "healthcare", "education", "travel", "subscription"
]

# Merchants by category
merchants = {
    "groceries": ["Whole Foods", "Safeway", "Kroger", "Trader Joe's"],
    "dining": ["McDonald's", "Starbucks", "Chipotle", "Local Restaurant"],
    "entertainment": ["Netflix", "Movie Theater", "Concert Venue", "Theme Park"],
    "utilities": ["Electric Company", "Water Service", "Gas Company", "Internet Provider"],
    "rent": ["Apartment Complex", "Property Management"],
    "mortgage": ["Bank of America", "Wells Fargo", "Chase"],
    "transportation": ["Uber", "Lyft", "Gas Station", "Public Transit"],
    "shopping": ["Amazon", "Target", "Walmart", "Best Buy"],
    "healthcare": ["Pharmacy", "Doctor's Office", "Hospital", "Dental Clinic"],
    "education": ["University", "Online Course", "Bookstore"],
    "travel": ["Airline", "Hotel", "Car Rental", "Travel Agency"],
    "subscription": ["Gym Membership", "Magazine", "Software Service"]
}

def generate_mock_transactions(user_id, num_transactions=30):
    """Generate mock transactions for a user"""
    transactions_list = []
    
    # Generate transactions spanning the last 30 days
    for i in range(num_transactions):
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        transaction_date = datetime.now() - timedelta(days=days_ago)
        
        # Random category and merchant
        category = random.choice(transaction_categories)
        merchant = random.choice(merchants.get(category, ["Unknown"]))
        
        # Amount based on category
        if category in ["rent", "mortgage"]:
            amount = random.uniform(1000, 2500)
        elif category in ["utilities", "transportation", "healthcare"]:
            amount = random.uniform(50, 300)
        elif category in ["groceries", "dining", "shopping"]:
            amount = random.uniform(10, 200)
        else:
            amount = random.uniform(5, 100)
        
        # Create transaction
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_id,
            "amount": round(amount, 2),
            "category": category,
            "merchant": merchant,
            "timestamp": transaction_date,
            "description": f"Purchase at {merchant}"
        }
        
        transactions_list.append(transaction)
    
    return transactions_list

async def populate_mock_data():
    """Populate database with mock data"""
    # Check if data already exists
    if products.count_documents({}) > 0:
        print("Mock data already exists. Skipping...")
        return
    
    # Insert products
    products.insert_many(sample_products)
    print(f"Inserted {len(sample_products)} products")
    
    # Insert users
    users.insert_many(sample_users)
    print(f"Inserted {len(sample_users)} users")
    
    # Generate and insert transactions for each user
    for user in sample_users:
        user_transactions = generate_mock_transactions(user["user_id"])
        transactions.insert_many(user_transactions)
        print(f"Inserted {len(user_transactions)} transactions for {user['name']}")
    
    print("Mock data population complete!")