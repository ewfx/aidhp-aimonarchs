# app/services/sentiment_service.py
import re
import random

class SentimentService:
    _instance = None
    analyzer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentService, cls).__new__(cls)
            try:
                # Import transformer conditionally to avoid startup errors
                from transformers import pipeline
                
                # Use a lightweight sentiment analysis model
                cls._instance.analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
                print("Loaded sentiment analysis model")
            except Exception as e:
                print(f"Error loading sentiment model (using rule-based fallback): {e}")
                cls._instance.analyzer = None
        return cls._instance
    
    def analyze_transaction_sentiment(self, transactions):
        """
        Analyze financial sentiment from transaction data
        """
        if not transactions:
            return {
                "overall_sentiment": "neutral",
                "confidence": 0.5,
                "financial_health": "stable"
            }
        
        # Always use rule-based for now to avoid errors
        return self._rule_based_sentiment(transactions)
        
        # This code is temporarily commented out to avoid errors
        # if not self.analyzer:
        #    # Fallback to rule-based sentiment
        #    return self._rule_based_sentiment(transactions)
        
        # The transformer-based code would go here, but we're skipping for now
    
    def _rule_based_sentiment(self, transactions):
        """
        Fallback rule-based sentiment analysis
        """
        # Calculate total spent
        total_spent = sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) > 0)
        
        # Count transactions by category
        categories = {}
        for t in transactions:
            cat = t.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Check for concerning patterns
        essential_spending = sum(t.get("amount", 0) for t in transactions 
                                if t.get("category") in ["groceries", "utilities", "rent", "mortgage", "healthcare"])
        luxury_spending = sum(t.get("amount", 0) for t in transactions 
                             if t.get("category") in ["entertainment", "dining", "shopping", "travel"])
        
        # Simple heuristic for financial health
        try:
            ratio = essential_spending / (luxury_spending + 0.01)  # Avoid division by zero
        except:
            ratio = 1.0
        
        if ratio > 5:
            financial_health = "cautious"
            sentiment = "negative"
            confidence = 0.7
        elif ratio < 0.5:
            financial_health = "indulgent"
            sentiment = "positive" if luxury_spending < 5000 else "concerning"
            confidence = 0.6
        else:
            financial_health = "balanced"
            sentiment = "positive"
            confidence = 0.8
        
        return {
            "overall_sentiment": sentiment,
            "confidence": confidence,
            "financial_health": financial_health
        }
    
    def _determine_financial_health(self, transactions):
        """
        Determine financial health based on transaction patterns
        """
        # Count transactions by category
        categories = {}
        for t in transactions:
            cat = t.get("category", "other")
            amount = t.get("amount", 0)
            categories[cat] = categories.get(cat, 0) + amount
        
        # Check balance between essential and discretionary spending
        essentials = sum(categories.get(cat, 0) for cat in ["groceries", "utilities", "rent", "mortgage", "healthcare"])
        discretionary = sum(categories.get(cat, 0) for cat in ["entertainment", "dining", "shopping", "travel"])
        
        # Check recurring payments and savings
        recurring = sum(categories.get(cat, 0) for cat in ["subscription", "utilities"])
        savings = categories.get("savings", 0)
        
        # Determine health
        total_values = sum(categories.values()) or 1  # Avoid division by zero
        
        if savings > 0 and essentials < 0.6 * total_values:
            return "excellent"
        elif essentials < 0.7 * total_values and discretionary < 0.4 * total_values:
            return "good"
        elif essentials > 0.8 * total_values:
            return "stressed"
        elif discretionary > 0.5 * total_values:
            return "overspending"
        else:
            return "stable"