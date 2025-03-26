# app/db/user_operations.py
from app.db.connection import db
from datetime import datetime, timedelta
import uuid
import random

# Collection reference
users_collection = db.users

class ProductOperations:
    @staticmethod
    def create_product(product_data):
        """
        Create a new product in the database
        
        Args:
            product_data (dict): Product data to insert
            
        Returns:
            str: ID of the created product
        """
        # Add timestamps if not provided
        if "created_at" not in product_data:
            product_data["created_at"] = datetime.now()
        
        if "updated_at" not in product_data:
            product_data["updated_at"] = datetime.now()
        
        # Generate product_id if not provided
        if "product_id" not in product_data:
            product_data["product_id"] = str(uuid.uuid4())
        
        # Set default is_active if not provided
        if "is_active" not in product_data:
            product_data["is_active"] = True
            
        result = products_collection.insert_one(product_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_product_by_id(product_id):
        """
        Get a product by its ID
        
        Args:
            product_id (str): Product ID to search for
            
        Returns:
            dict: Product document or None if not found
        """
        return products_collection.find_one({"product_id": product_id})
    
    @staticmethod
    def get_products(category=None, active_only=True, limit=0):
        """
        Get products with optional filtering
        
        Args:
            category (str, optional): Filter by category
            active_only (bool): Only include active products
            limit (int): Maximum number of products to return (0 for all)
            
        Returns:
            list: List of product documents
        """
        query = {}
        
        if category:
            query["category"] = category
        
        if active_only:
            query["is_active"] = True
        
        cursor = products_collection.find(query)
        
        if limit > 0:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    @staticmethod
    def update_product(product_id, update_data):
        """
        Update a product
        
        Args:
            product_id (str): Product ID to update
            update_data (dict): Data to update
            
        Returns:
            bool: True if update was successful
        """
        # Update the updated_at timestamp
        update_data["updated_at"] = datetime.now()
        
        result = products_collection.update_one(
            {"product_id": product_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_product(product_id):
        """
        Delete a product
        
        Args:
            product_id (str): Product ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        result = products_collection.delete_one({"product_id": product_id})
        return result.deleted_count > 0
    
    @staticmethod
    def deactivate_product(product_id):
        """
        Deactivate a product (instead of deleting)
        
        Args:
            product_id (str): Product ID to deactivate
            
        Returns:
            bool: True if deactivation was successful
        """
        result = products_collection.update_one(
            {"product_id": product_id},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_products_by_eligibility(income=None, credit_score=None, risk_level=None, age=None):
        """
        Get products matching specific eligibility criteria
        
        Args:
            income (float, optional): User income
            credit_score (int, optional): User credit score
            risk_level (str, optional): User risk profile
            age (int, optional): User age
            
        Returns:
            list: List of matching product documents
        """
        query = {"is_active": True}
        
        # Add eligibility criteria if provided
        if income is not None:
            query["eligibility.min_income"] = {"$lte": income}
        
        if credit_score is not None:
            query["eligibility.min_credit_score"] = {"$lte": credit_score}
        
        if risk_level is not None:
            query["eligibility.risk_level"] = risk_level
        
        if age is not None:
            query["$and"] = [
                {"$or": [
                    {"eligibility.target_age_min": {"$exists": False}},
                    {"eligibility.target_age_min": {"$lte": age}}
                ]},
                {"$or": [
                    {"eligibility.target_age_max": {"$exists": False}},
                    {"eligibility.target_age_max": {"$gte": age}}
                ]}
            ]
        
        return list(products_collection.find(query))


def insert_dummy_products(count=5):
    """
    Insert dummy product data
    
    Args:
        count (int): Number of products to create
        
    Returns:
        list: List of created product documents
    """
    # Sample product data templates
    product_templates = [
        {
            "name": "Premium Savings Account",
            "category": "Savings",
            "description": "High-yield savings account with competitive rates",
            "features": ["No minimum balance", "No monthly fees", "2.5% APY"],
            "details": {
                "interest_rate": 2.5,
                "min_balance": 0,
                "monthly_fee": 0,
                "early_withdrawal_penalty": True
            },
            "eligibility": {
                "min_income": 0,
                "min_credit_score": 680,
                "risk_level": "moderate",
                "target_age_min": 18,
                "target_age_max": 65
            }
        },
        {
            "name": "Growth Investment Fund",
            "category": "Investments",
            "description": "Diversified investment fund for long-term growth",
            "features": ["Professionally managed", "Quarterly rebalancing", "12.3% average return"],
            "details": {
                "average_return": 12.3,
                "expense_ratio": 0.75,
                "min_investment": 1000,
                "liquidity": "Medium"
            },
            "eligibility": {
                "min_income": 75000,
                "min_credit_score": 720,
                "risk_level": "aggressive",
                "target_age_min": 25,
                "target_age_max": 45
            }
        },
        {
            "name": "Travel Rewards Credit Card",
            "category": "Credit Cards",
            "description": "Premium travel rewards credit card with no foreign transaction fees",
            "features": ["No foreign transaction fees", "50,000 bonus points", "Free travel insurance"],
            "details": {
                "annual_fee": 95,
                "apr": 17.99,
                "rewards_rate": "3x on travel and dining",
                "credit_limit_min": 5000,
                "credit_limit_max": 25000
            },
            "eligibility": {
                "min_income": 60000,
                "min_credit_score": 740,
                "risk_level": "moderate",
                "target_age_min": 21,
                "target_age_max": 65
            }
        },
        {
            "name": "Home Mortgage",
            "category": "Loans",
            "description": "Fixed-rate home mortgage with competitive rates",
            "features": ["Fixed rate", "15-30 year terms", "No prepayment penalties"],
            "details": {
                "interest_rate_range": [3.5, 4.5],
                "loan_term_range": [15, 30],
                "max_loan_amount": 1000000,
                "prepayment_penalty": False
            },
            "eligibility": {
                "min_income": 50000,
                "min_credit_score": 680,
                "risk_level": "moderate",
                "target_age_min": 25,
                "target_age_max": 65
            }
        },
        {
            "name": "Retirement Plan",
            "category": "Retirement",
            "description": "Long-term retirement savings with tax advantages",
            "features": ["Tax advantages", "Employer matching", "Regular contributions"],
            "details": {
                "contribution_limit": 19500,
                "tax_deferred": True,
                "early_withdrawal_penalty": "10%",
                "investment_options": ["Stocks", "Bonds", "ETFs", "Mutual Funds"]
            },
            "eligibility": {
                "min_income": 0,
                "min_credit_score": 0,
                "risk_level": "moderate",
                "target_age_min": 18,
                "target_age_max": 65
            }
        },
        {
            "name": "Student Loan Refinancing",
            "category": "Loans",
            "description": "Lower your student loan interest rate and monthly payment",
            "features": ["No origination fees", "Flexible repayment terms", "Rate discount with autopay"],
            "details": {
                "interest_rate_range": [2.99, 5.99],
                "loan_term_range": [5, 20],
                "min_loan_amount": 5000,
                "max_loan_amount": 300000
            },
            "eligibility": {
                "min_income": 35000,
                "min_credit_score": 680,
                "risk_level": "conservative",
                "target_age_min": 21,
                "target_age_max": 45
            }
        },
        {
            "name": "High-Yield Checking Account",
            "category": "Checking",
            "description": "Earn interest on your checking account balance",
            "features": ["No minimum balance", "No monthly fees", "1.5% APY on balances up to $25,000"],
            "details": {
                "interest_rate": 1.5,
                "min_balance": 0,
                "monthly_fee": 0,
                "atm_fee_refunds": True
            },
            "eligibility": {
                "min_income": 0,
                "min_credit_score": 0,
                "risk_level": "conservative",
                "target_age_min": 18,
                "target_age_max": 99
            }
        }
    ]
    
    # Insert products based on templates
    created_products = []
    
    # Use either the templates provided or a subset if count is smaller
    templates_to_use = random.sample(product_templates, min(count, len(product_templates)))
    
    for i, template in enumerate(templates_to_use):
        product = template.copy()
        
        # Add unique product ID and timestamps
        product["product_id"] = f"prod{i+1}"
        product["created_at"] = datetime.now()
        product["updated_at"] = datetime.now()
        product["is_active"] = True
        
        # Insert the product
        products_collection.insert_one(product)
        created_products.append(product)
    
    print(f"Created {len(created_products)} dummy products")
    return created_products


if __name__ == "__main__":
    # Test the functions
    print("Inserting dummy products...")
    insert_dummy_products(7)
    print("Done!")