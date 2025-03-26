from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URL"))
db = client[os.getenv("DB_NAME")]

# Collections
users = db.users
transactions = db.transactions
products = db.products
recommendations = db.recommendations

# Test connection
def test_connection():
    try:
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False