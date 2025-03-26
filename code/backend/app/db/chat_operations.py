# app/db/user_operations.py
from app.db.connection import db
from datetime import datetime, timedelta
import uuid
import random

# Collection reference
users_collection = db.users

class ChatOperations:
    @staticmethod
    def create_message(message_data):
        """
        Create a new chat message in the database
        
        Args:
            message_data (dict): Message data to insert
            
        Returns:
            str: ID of the created message
        """
        # Add timestamp if not provided
        if "timestamp" not in message_data:
            message_data["timestamp"] = datetime.now()
        
        # Generate message_id if not provided
        if "message_id" not in message_data:
            message_data["message_id"] = str(uuid.uuid4())
        
        # Generate conversation_id if not provided
        if "conversation_id" not in message_data:
            message_data["conversation_id"] = str(uuid.uuid4())
            
        result = chat_messages_collection.insert_one(message_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_message_by_id(message_id):
        """
        Get a message by its ID
        
        Args:
            message_id (str): Message ID to search for
            
        Returns:
            dict: Message document or None if not found
        """
        return chat_messages_collection.find_one({"message_id": message_id})
    
    @staticmethod
    def get_user_conversations(user_id):
        """
        Get all conversations for a user
        
        Args:
            user_id (str): User ID to filter by
            
        Returns:
            list: List of distinct conversation IDs
        """
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$conversation_id"}},
            {"$project": {"conversation_id": "$_id", "_id": 0}}
        ]
        
        result = chat_messages_collection.aggregate(pipeline)
        return [doc["conversation_id"] for doc in result]
    
    @staticmethod
    def get_conversation_messages(conversation_id, limit=50):
        """
        Get messages for a specific conversation
        
        Args:
            conversation_id (str): Conversation ID to filter by
            limit (int): Maximum number of messages to return
            
        Returns:
            list: List of message documents in chronological order
        """
        cursor = chat_messages_collection.find({"conversation_id": conversation_id})
        
        # Sort by timestamp (oldest first)
        cursor = cursor.sort("timestamp", ASCENDING)
        
        # Apply limit if specified
        if limit > 0:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    @staticmethod
    def get_user_messages(user_id, limit=50):
        """
        Get most recent messages for a user across all conversations
        
        Args:
            user_id (str): User ID to filter by
            limit (int): Maximum number of messages to return
            
        Returns:
            list: List of message documents in reverse chronological order
        """
        cursor = chat_messages_collection.find({"user_id": user_id})
        
        # Sort by timestamp (newest first)
        cursor = cursor.sort("timestamp", -1)
        
        # Apply limit
        cursor = cursor.limit(limit)
        
        return list(cursor)
    
    @staticmethod
    def update_message(message_id, update_data):
        """
        Update a message
        
        Args:
            message_id (str): Message ID to update
            update_data (dict): Data to update
            
        Returns:
            bool: True if update was successful
        """
        result = chat_messages_collection.update_one(
            {"message_id": message_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_message(message_id):
        """
        Delete a message
        
        Args:
            message_id (str): Message ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        result = chat_messages_collection.delete_one({"message_id": message_id})
        return result.deleted_count > 0
    
    @staticmethod
    def delete_conversation(conversation_id):
        """
        Delete an entire conversation
        
        Args:
            conversation_id (str): Conversation ID to delete
            
        Returns:
            int: Number of messages deleted
        """
        result = chat_messages_collection.delete_many({"conversation_id": conversation_id})
        return result.deleted_count


def insert_dummy_chat_messages(user_ids, messages_per_user=4):
    """
    Insert dummy chat message data for specified users
    
    Args:
        user_ids (list): List of user IDs to create chat messages for
        messages_per_user (int): Number of messages per user
        
    Returns:
        int: Number of messages created
    """
    total_created = 0
    
    # Sample user queries and assistant responses
    user_queries = [
        "How much am I spending on dining out each month?",
        "What's the best way for me to save for a home down payment?",
        "How can I reduce my monthly expenses?",
        "Am I on track for retirement?",
        "Should I pay off my credit card debt or invest more?",
        "How much should I be saving each month?",
        "What's the difference between a Roth IRA and a traditional IRA?",
        "How can I improve my credit score?"
    ]
    
    assistant_responses = {
        "How much am I spending on dining out each month?": 
            "In the last 3 months, you've spent an average of $428 per month on dining out. This represents about 12% of your total monthly expenses. This is 15% higher than the previous 3 months, when you averaged $372 per month on dining.",
        
        "What's the best way for me to save for a home down payment?":
            "Based on your financial profile and goal to purchase a home in the next 3 years, I recommend:\n\n1. Increase your monthly savings by $300 by reducing entertainment expenses\n2. Open a high-yield savings account for your down payment fund (Premium Savings Account has a 2.5% APY)\n3. Set up automatic transfers of $850/month to this account\n\nThis approach will help you save approximately $32,400 in 3 years, plus interest, which would be sufficient for a 10% down payment on a $320,000 home.",
        
        "How can I reduce my monthly expenses?":
            "Based on your transaction history, here are 3 opportunities to reduce your monthly expenses:\n\n1. Subscription services: You're spending $65/month on services you rarely use\n2. Dining out: Reducing dining out by just 1 meal per week would save $160/month\n3. Groceries: Shopping at a different store could save about $85/month based on local price comparisons\n\nImplementing these changes could save you approximately $310 per month.",
        
        "Am I on track for retirement?":
            "Based on your current savings rate of 10% of income and your retirement accounts totaling $85,000, you're currently on track to reach about 65% of your needed retirement income by age 65. To reach your full retirement goal, consider:\n\n1. Increasing your contribution rate to 15%\n2. Maximizing your employer match benefit\n3. Exploring catch-up contributions when eligible\n\nMaking these changes could potentially close the gap and allow you to retire comfortably at your target age.",
        
        "Should I pay off my credit card debt or invest more?":
            "With your credit card interest rate at 18.99%, prioritizing debt repayment before additional investments would be financially optimal. Your investment returns average 8-10%, which is less than your debt interest cost. I recommend:\n\n1. Maintain your current retirement contributions to get employer matching\n2. Direct extra funds to pay down credit card debt\n3. Once debt is eliminated, redirect those payments to investments\n\nThis strategy would save you approximately $2,800 in interest over the next year.",
        
        "How much should I be saving each month?":
            "Based on your monthly income of $5,400 and expenses of $4,100, a healthy savings target would be $750-$850 per month (about 15% of your income). Currently, you're saving about $500/month, which is good but could be optimized. Consider:\n\n1. Emergency fund: Maintain 3-6 months of expenses ($12,300-$24,600)\n2. Retirement: Continue 10% contribution plus employer match\n3. Short-term goals: Allocate remaining savings to your travel fund\n\nThis balanced approach ensures both short and long-term financial security.",
        
        "What's the difference between a Roth IRA and a traditional IRA?":
            "The main differences are:\n\n1. Tax treatment: Traditional IRA contributions are tax-deductible now, but withdrawals are taxed in retirement. Roth IRA contributions are not tax-deductible, but qualified withdrawals are tax-free.\n\n2. Income limits: Roth IRAs have income eligibility limits, while anyone with earned income can contribute to a Traditional IRA.\n\n3. Required withdrawals: Traditional IRAs require minimum distributions (RMDs) starting at age 72, while Roth IRAs don't require withdrawals during your lifetime.\n\nGiven your current tax bracket and long-term goals, a Roth IRA might be more advantageous for you.",
        
        "How can I improve my credit score?":
            "Based on your credit profile, here are specific actions to improve your score:\n\n1. Reduce credit utilization: Your cards are at 45% utilization; aim for below 30%\n2. Address the late payment from March: Contact the creditor to request a goodwill adjustment\n3. Avoid opening new accounts: Your average account age is relatively low\n\nImplementing these changes could potentially increase your score by 30-50 points within 3-6 months."
    }
    
    # Generic responses for queries not in the predefined list
    generic_responses = [
        "Based on your financial data, I recommend focusing on building your emergency fund before increasing investments.",
        "Looking at your spending patterns, you could optimize your budget by reducing discretionary spending by about 15%.",
        "Your income has increased 8% since last year, which presents an opportunity to increase your retirement contributions.",
        "I notice you have several subscription services with overlapping features. Consolidating these could save you $45 monthly."
    ]
    
    for user_id in user_ids:
        # Create a conversation ID for this user
        conversation_id = str(uuid.uuid4())
        
        # Generate a dialogue with alternating user and assistant messages
        for i in range(messages_per_user // 2):
            # Select a random query
            query = random.choice(user_queries)
            
            # Get the paired response or a generic one
            response_text = assistant_responses.get(query, random.choice(generic_responses))
            
            # Timestamp for the user message
            user_timestamp = datetime.now() - timedelta(minutes=(messages_per_user - (i*2)) * 5)
            
            # Create user message
            user_message = {
                "message_id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "user_id": user_id,
                "sender": "user",
                "text": query,
                "timestamp": user_timestamp,
                "intent": None,
                "entities": [],
                "context": {},
                "metadata": {
                    "client_info": {
                        "device": random.choice(["mobile", "desktop", "tablet"]),
                        "platform": random.choice(["ios", "android", "web"])
                    }
                }
            }
            
            # Create assistant message (response to user query)
            assistant_message = {
                "message_id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "user_id": user_id,
                "sender": "assistant",
                "text": response_text,
                "timestamp": user_timestamp + timedelta(minutes=1),
                "intent": None,
                "entities": [],
                "context": {
                    "previous_message_id": user_message["message_id"]
                },
                "metadata": {}
            }
            
            # Insert the messages
            chat_messages_collection.insert_one(user_message)
            chat_messages_collection.insert_one(assistant_message)
            total_created += 2
    
    print(f"Created {total_created} dummy chat messages for {len(user_ids)} users")
    return total_created


if __name__ == "__main__":
    # Test the functions
    from user_operations import UserOperations
    
    # Get some user IDs
    users = list(db.users.find({}, {"user_id": 1}).limit(3))
    user_ids = [user["user_id"] for user in users]
    
    if not user_ids:
        print("No users found. Creating some dummy users first...")
        from user_operations import insert_dummy_users
        user_ids = insert_dummy_users(3)
    
    print("Inserting dummy chat messages...")
    insert_dummy_chat_messages(user_ids, 6)
    print("Done!")