from app.db.connection import db
from datetime import datetime, timedelta
import uuid
import random
from pymongo import ASCENDING, DESCENDING

# Collection reference
transactions_collection = db.transactions

class TransactionOperations:
    @staticmethod
    def create_transaction(transaction_data):
        """
        Create a new transaction in the database
        
        Args:
            transaction_data (dict): Transaction data to insert
            
        Returns:
            str: ID of the created transaction
        """
        # Add timestamp if not provided
        if "timestamp" not in transaction_data:
            transaction_data["timestamp"] = datetime.now()
        
        # Generate transaction_id if not provided
        if "transaction_id" not in transaction_data:
            transaction_data["transaction_id"] = str(uuid.uuid4())
            
        result = transactions_collection.insert_one(transaction_data)
        return transaction_data["transaction_id"]
    
    @staticmethod
    def get_transaction_by_id(transaction_id):
        """
        Get a transaction by its ID
        
        Args:
            transaction_id (str): Transaction ID to search for
            
        Returns:
            dict: Transaction document or None if not found
        """
        return transactions_collection.find_one({"transaction_id": transaction_id})
    
    @staticmethod
    def get_user_transactions(user_id, limit=50, skip=0, sort_by="timestamp", sort_order=-1, 
                              start_date=None, end_date=None, category=None):
        """
        Get transactions for a specific user with optional filtering
        
        Args:
            user_id (str): User ID to filter by
            limit (int): Maximum number of transactions to return
            skip (int): Number of transactions to skip (for pagination)
            sort_by (str): Field to sort by
            sort_order (int): Sort order (1 for ascending, -1 for descending)
            start_date (datetime, optional): Filter by transactions after this date
            end_date (datetime, optional): Filter by transactions before this date
            category (str, optional): Filter by category
            
        Returns:
            list: List of transaction documents
        """
        # Build query
        query = {"user_id": user_id}
        
        # Add date range if provided
        if start_date or end_date:
            query["timestamp"] = {}
            
            if start_date:
                query["timestamp"]["$gte"] = start_date
                
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        # Add category filter if provided
        if category:
            query["category"] = category
        
        # Execute query with sorting and pagination
        cursor = transactions_collection.find(query)
        
        # Apply sorting
        cursor = cursor.sort(sort_by, sort_order)
        
        # Apply pagination
        cursor = cursor.skip(skip).limit(limit)
        
        return list(cursor)
    
    @staticmethod
    def get_user_transactions_in_date_range(user_id, start_date, end_date):
        """
        Get all transactions for a user within a date range
        
        Args:
            user_id (str): User ID to filter by
            start_date (datetime): Start date for filtering
            end_date (datetime): End date for filtering
            
        Returns:
            list: List of transaction documents
        """
        query = {
            "user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        return list(transactions_collection.find(query))
    
    @staticmethod
    def get_transactions_by_category(user_id, category, start_date=None, end_date=None):
        """
        Get transactions for a specific user and category within a date range
        
        Args:
            user_id (str): User ID to filter by
            category (str): Category to filter by
            start_date (datetime): Start date for filtering
            end_date (datetime): End date for filtering
            
        Returns:
            list: List of transaction documents
        """
        query = {"user_id": user_id, "category": category}
        
        # Add date range if provided
        if start_date or end_date:
            query["timestamp"] = {}
            
            if start_date:
                query["timestamp"]["$gte"] = start_date
                
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        return list(transactions_collection.find(query).sort("timestamp", DESCENDING))
    
    @staticmethod
    def update_transaction(transaction_id, update_data):
        """
        Update a transaction
        
        Args:
            transaction_id (str): Transaction ID to update
            update_data (dict): Data to update
            
        Returns:
            bool: True if update was successful
        """
        result = transactions_collection.update_one(
            {"transaction_id": transaction_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_transaction(transaction_id):
        """
        Delete a transaction
        
        Args:
            transaction_id (str): Transaction ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        result = transactions_collection.delete_one({"transaction_id": transaction_id})
        return result.deleted_count > 0
    
    @staticmethod
    def get_monthly_summary(user_id, year, month):
        """
        Get a monthly summary of transactions for a user
        
        Args:
            user_id (str): User ID to filter by
            year (int): Year to filter by
            month (int): Month to filter by
            
        Returns:
            dict: Monthly summary statistics
        """
        # Create date range for the specified month
        start_date = datetime(year, month, 1)
        
        # Calculate the last day of the month
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
        
        # Query for transactions in the specified month
        query = {
            "user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        # Get all transactions for the month
        transactions = list(transactions_collection.find(query))
        
        # Calculate total income and expenses
        income = sum(t["amount"] for t in transactions if t["amount"] > 0)
        expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
        
        # Calculate expenses by category
        expenses_by_category = {}
        for transaction in transactions:
            if transaction["amount"] < 0:
                category = transaction.get("category", "Uncategorized")
                expenses_by_category[category] = expenses_by_category.get(category, 0) + abs(transaction["amount"])
        
        return {
            "user_id": user_id,
            "year": year,
            "month": month,
            "income": income,
            "expenses": expenses,
            "net": income - expenses,
            "transaction_count": len(transactions),
            "expenses_by_category": expenses_by_category
        }
    
    @staticmethod
    def get_category_spending_trend(user_id, category, months=6):
        """
        Get a spending trend for a specific category over time
        
        Args:
            user_id (str): User ID to filter by
            category (str): Category to analyze
            months (int): Number of months to look back
            
        Returns:
            list: Monthly spending for the category
        """
        # Calculate the start date (months ago from today)
        end_date = datetime.now()
        start_date = datetime(end_date.year, end_date.month, 1) - timedelta(days=1)
        
        for _ in range(months - 1):
            start_date = datetime(start_date.year, start_date.month, 1) - timedelta(days=1)
        
        start_date = datetime(start_date.year, start_date.month, 1)
        
        # Get transactions for the category in the date range
        query = {
            "user_id": user_id,
            "category": category,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            },
            "amount": {"$lt": 0}  # Only consider expenses (negative amounts)
        }
        
        transactions = list(transactions_collection.find(query))
        
        # Group transactions by month
        monthly_spending = {}
        
        for transaction in transactions:
            date = transaction["timestamp"]
            month_key = f"{date.year}-{date.month:02d}"
            
            if month_key not in monthly_spending:
                monthly_spending[month_key] = {
                    "year": date.year,
                    "month": date.month,
                    "month_name": date.strftime("%b"),
                    "total": 0
                }
            
            monthly_spending[month_key]["total"] += abs(transaction["amount"])
        
        # Convert to sorted list
        result = sorted(monthly_spending.values(), key=lambda x: (x["year"], x["month"]))
        
        return result
    
    @staticmethod
    def get_user_categories(user_id):
        """
        Get all unique transaction categories used by a user
        
        Args:
            user_id (str): User ID to filter by
            
        Returns:
            list: List of unique categories
        """
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$category"}},
            {"$sort": {"_id": 1}}
        ]
        
        result = transactions_collection.aggregate(pipeline)
        return [doc["_id"] for doc in result if doc["_id"] is not None]

    @staticmethod
    def insert_dummy_transactions(user_ids, count_per_user=30):
        """
        Insert dummy transaction data for specified users
        
        Args:
            user_ids (list): List of user IDs to create transactions for
            count_per_user (int): Number of transactions per user
            
        Returns:
            int: Number of transactions created
        """
        total_created = 0
        
        # Sample data for variation
        categories = [
            "Groceries", "Dining", "Entertainment", "Utilities", 
            "Rent", "Mortgage", "Transportation", "Shopping", 
            "Healthcare", "Education", "Travel", "Subscription"
        ]
        
        merchants = {
            "Groceries": ["Whole Foods", "Safeway", "Kroger", "Trader Joe's"],
            "Dining": ["McDonald's", "Starbucks", "Chipotle", "Local Restaurant"],
            "Entertainment": ["Netflix", "Movie Theater", "Concert Venue", "Theme Park"],
            "Utilities": ["Electric Company", "Water Service", "Gas Company", "Internet Provider"],
            "Rent": ["Apartment Complex", "Property Management"],
            "Mortgage": ["Bank of America", "Wells Fargo", "Chase"],
            "Transportation": ["Uber", "Lyft", "Gas Station", "Public Transit"],
            "Shopping": ["Amazon", "Target", "Walmart", "Best Buy"],
            "Healthcare": ["Pharmacy", "Doctor's Office", "Hospital", "Dental Clinic"],
            "Education": ["University", "Online Course", "Bookstore"],
            "Travel": ["Airline", "Hotel", "Car Rental", "Travel Agency"],
            "Subscription": ["Gym Membership", "Magazine", "Software Service"]
        }
        
        payment_methods = ["Credit Card", "Debit Card", "Bank Transfer", "Cash", "Mobile Payment"]
        
        for user_id in user_ids:
            # Generate transactions for this user
            for _ in range(count_per_user):
                # Random date within last 90 days
                days_ago = random.randint(0, 90)
                transaction_date = datetime.now() - timedelta(days=days_ago)
                
                # Random category and merchant
                category = random.choice(categories)
                merchant = random.choice(merchants.get(category, ["Unknown"]))
                
                # Determine if it's income or expense (20% chance of income)
                is_income = random.random() < 0.2
                
                # Amount based on category
                if is_income:
                    amount = random.uniform(1000, 5000)
                    category = "Income"
                    merchant = random.choice(["Payroll", "Freelance", "Dividends", "Interest", "Gift"])
                elif category in ["Rent", "Mortgage"]:
                    amount = -1 * random.uniform(1000, 2500)
                elif category in ["Utilities", "Transportation", "Healthcare"]:
                    amount = -1 * random.uniform(50, 300)
                elif category in ["Groceries", "Dining", "Shopping"]:
                    amount = -1 * random.uniform(10, 200)
                else:
                    amount = -1 * random.uniform(5, 100)
                
                # Create transaction
                transaction = {
                    "transaction_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "amount": round(amount, 2),
                    "description": f"{merchant} {'Payment' if amount < 0 else 'Deposit'}",
                    "category": category,
                    "merchant": merchant,
                    "timestamp": transaction_date,
                    "location": {
                        "city": random.choice(["New York", "San Francisco", "Chicago", "Austin"]),
                        "state": random.choice(["NY", "CA", "IL", "TX"])
                    },
                    "payment_method": random.choice(payment_methods),
                    "account_id": f"acc{random.randint(100, 999)}",
                    "tags": random.sample(["essential", "discretionary", "recurring", "one-time"], k=random.randint(0, 2)),
                    "is_recurring": random.random() < 0.3,
                    "notes": ""
                }
                
                # Insert the transaction
                transactions_collection.insert_one(transaction)
                total_created += 1
        
        print(f"Created {total_created} dummy transactions for {len(user_ids)} users")
        return total_created

    # This allows you to run this file directly to insert dummy data
    if __name__ == "__main__":
        # Test the functions
        from app.db.user_operations import UserOperations
        
        # Get some user IDs
        users = list(db.users.find({}, {"user_id": 1}).limit(3))
        user_ids = [user["user_id"] for user in users]
        
        if not user_ids:
            print("No users found. Creating some dummy users first...")
            from app.db.user_operations import insert_dummy_users
            user_ids = insert_dummy_users(3)
        
        print("Inserting dummy transactions...")
        insert_dummy_transactions(user_ids, 40)
        print("Done!")