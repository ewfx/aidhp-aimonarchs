from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# User Profile Schema
class UserProfile(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    age: Optional[int] = None
    income_bracket: Optional[str] = None
    balance: Optional[str] = None
    risk_profile: Optional[str] = None
    financial_goals: Optional[List[str]] = []
    preferred_categories: Optional[List[str]] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Transaction Schema
class Transaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    category: str
    merchant: str
    timestamp: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = None

# Product Schema
class Product(BaseModel):
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    description: str
    features: List[str]
    min_income: Optional[float] = None
    risk_level: Optional[str] = None
    target_age_min: Optional[int] = None
    target_age_max: Optional[int] = None

# Recommendation Schema
class Recommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    score: float
    reason: str
    timestamp: datetime = Field(default_factory=datetime.now)
    is_viewed: bool = False
    is_clicked: bool = False
    features: Optional[str] = None