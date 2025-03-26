from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import uuid

from app.db.user_operations import UserOperations
from app.db.transaction_operations import TransactionOperations
from app.services.genai_services import GenAIService

logger = logging.getLogger(__name__)

class TransactionIntelligenceService:
    """
    Transaction intelligence service using GenAI to analyze transactions
    and provide advanced insights, anomaly detection, and predictions
    """
    
    def __init__(self):
        """Initialize transaction intelligence service with GenAI service"""
        self.genai_service = GenAIService()
    
    async def detect_anomalies(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Detect anomalies in user transactions
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            List of anomalies detected
        """
        try:
            # Get recent transactions (last 90 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = TransactionOperations.get_user_transactions_in_date_range(
                user_id, start_date, end_date
            )
            
            if not transactions or len(transactions) < 10:
                # Not enough data for meaningful analysis
                logger.info(f"Not enough transaction data for user {user_id} to detect anomalies")
                return []
            
            # Use GenAI to detect anomalies
            anomalies = await self.genai_service.detect_anomalies(transactions)
            
            # Update user profile with detected anomalies
            if anomalies:
                user = UserOperations.get_user_by_id(user_id)
                if user:
                    # Get existing anomalies
                    existing_anomalies = user.get("anomalies", [])
                    
                    # Add new anomalies
                    for anomaly in anomalies:
                        # Add anomaly ID and detection date if not present
                        if "anomaly_id" not in anomaly:
                            anomaly["anomaly_id"] = f"ano{len(existing_anomalies) + 1}_{user_id[:8]}"
                        
                        if "detection_date" not in anomaly:
                            anomaly["detection_date"] = datetime.now()
                        
                        anomaly["is_acknowledged"] = False
                        existing_anomalies.append(anomaly)
                    
                    # Update user profile
                    UserOperations.update_user(user_id, {"anomalies": existing_anomalies})
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies for user {user_id}: {str(e)}")
            return []
    
    async def predict_expenses(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Predict upcoming expenses for a user
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            List of predicted expenses
        """
        try:
            # Get transaction history (last 6 months)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            transactions = TransactionOperations.get_user_transactions_in_date_range(
                user_id, start_date, end_date
            )
            
            if not transactions or len(transactions) < 10:
                # Not enough data for meaningful predictions
                logger.info(f"Not enough transaction data for user {user_id} to predict expenses")
                return []
            
            # Use GenAI to predict expenses
            predicted_expenses = await self.genai_service.generate_predictive_expenses(transactions)
            
            # Update user profile with predicted expenses
            if predicted_expenses:
                user = UserOperations.get_user_by_id(user_id)
                if user:
                    # Replace existing predicted expenses
                    UserOperations.update_user(user_id, {"predicted_expenses": predicted_expenses})
            
            return predicted_expenses
            
        except Exception as e:
            logger.error(f"Error predicting expenses for user {user_id}: {str(e)}")
            return []
    
    async def analyze_spending_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze spending patterns for a user
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Dict with spending pattern analysis
        """
        try:
            # Get recent transactions (last 90 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = TransactionOperations.get_user_transactions_in_date_range(
                user_id, start_date, end_date
            )
            
            if not transactions:
                return {
                    "error": "Not enough transaction data for analysis",
                    "patterns": []
                }
            
            # Group transactions by category
            categories = {}
            total_spent = 0
            
            for txn in transactions:
                if txn.get("amount", 0) >= 0:  # Skip income
                    continue
                    
                amount = abs(txn.get("amount", 0))
                category = txn.get("category", "Other")
                
                if category not in categories:
                    categories[category] = {
                        "total": 0,
                        "count": 0,
                        "transactions": []
                    }
                
                categories[category]["total"] += amount
                categories[category]["count"] += 1
                categories[category]["transactions"].append(txn)
                
                total_spent += amount
            
            # Calculate percentages and analyze each category
            patterns = []
            
            for category, data in categories.items():
                if total_spent > 0:
                    percentage = (data["total"] / total_spent) * 100
                else:
                    percentage = 0
                
                # Get category trend
                trend = TransactionOperations.get_category_spending_trend(
                    user_id, category, months=3
                )
                
                # Determine trend direction
                trend_direction = "stable"
                if len(trend) >= 2:
                    latest = trend[-1]["total"] if trend else 0
                    previous = trend[-2]["total"] if len(trend) > 1 else 0
                    
                    if latest > previous * 1.1:  # 10% increase
                        trend_direction = "increasing"
                    elif latest < previous * 0.9:  # 10% decrease
                        trend_direction = "decreasing"
                
                pattern = {
                    "category": category,
                    "total": data["total"],
                    "count": data["count"],
                    "percentage": round(percentage, 1),
                    "average_transaction": round(data["total"] / data["count"], 2) if data["count"] > 0 else 0,
                    "trend_direction": trend_direction,
                    "trend_data": trend
                }
                
                patterns.append(pattern)
            
            # Sort patterns by total amount spent (descending)
            patterns = sorted(patterns, key=lambda x: x["total"], reverse=True)
            
            return {
                "user_id": user_id,
                "period": "90 days",
                "start_date": start_date,
                "end_date": end_date,
                "total_spent": total_spent,
                "pattern_count": len(patterns),
                "patterns": patterns
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns for user {user_id}: {str(e)}")
            return {"error": f"Failed to analyze spending patterns: {str(e)}"}
    
    async def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Improve transaction categorization using GenAI
        
        Args:
            transactions: List of transactions to categorize
            
        Returns:
            List of transactions with updated categories
        """
        # This would typically use a specialized GenAI method for categorization
        # For now, we'll implement a simple rule-based categorization
        
        # Common merchant to category mappings
        merchant_categories = {
            "walmart": "Groceries",
            "target": "Shopping",
            "amazon": "Shopping",
            "netflix": "Entertainment",
            "spotify": "Entertainment",
            "uber": "Transportation",
            "lyft": "Transportation",
            "starbucks": "Dining",
            "mcdonald": "Dining",
            "chipotle": "Dining",
            "shell": "Transportation",
            "exxon": "Transportation",
            "at&t": "Utilities",
            "verizon": "Utilities",
            "comcast": "Utilities",
            "rent": "Housing",
            "mortgage": "Housing",
            "cvs": "Healthcare",
            "walgreens": "Healthcare"
        }
        
        updated_transactions = []
        
        for txn in transactions:
            # Get merchant name and description
            merchant = txn.get("merchant", "").lower()
            description = txn.get("description", "").lower()
            
            # Check if transaction already has a category
            if txn.get("category") and txn.get("category") != "Uncategorized":
                # Keep existing category
                updated_transactions.append(txn)
                continue
            
            # Try to match merchant to category
            assigned_category = None
            
            for key, category in merchant_categories.items():
                if key in merchant or key in description:
                    assigned_category = category
                    break
            
            # If no match found, use a default category
            if not assigned_category:
                if txn.get("amount", 0) >= 0:
                    assigned_category = "Income"
                else:
                    assigned_category = "Miscellaneous"
            
            # Create updated transaction with new category
            updated_txn = txn.copy()
            updated_txn["category"] = assigned_category
            
            updated_transactions.append(updated_txn)
        
        return updated_transactions
    
    async def generate_monthly_report(self, user_id: str, year: int, month: int) -> Dict[str, Any]:
        """
        Generate a comprehensive monthly financial report
        
        Args:
            user_id: User ID
            year: Year for the report
            month: Month for the report
            
        Returns:
            Dict with monthly report data
        """
        try:
            # Get monthly summary
            monthly_summary = TransactionOperations.get_monthly_summary(user_id, year, month)
            
            # Get user profile
            user = UserOperations.get_user_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Calculate budget performance
            income = monthly_summary.get("income", 0)
            expenses = monthly_summary.get("expenses", 0)
            net = income - expenses
            
            # Get target budget from user profile if available
            budget_target = user.get("financial_profile", {}).get("monthly_expenses", 0)
            
            if budget_target > 0:
                budget_performance = (expenses / budget_target) * 100
                budget_status = "under_budget" if expenses <= budget_target else "over_budget"
            else:
                budget_performance = 0
                budget_status = "no_budget"
            
            # Calculate savings rate
            if income > 0:
                savings_rate = (net / income) * 100
            else:
                savings_rate = 0
            
            # Get month name
            month_name = datetime(year, month, 1).strftime("%B")
            
            # Generate report
            report = {
                "user_id": user_id,
                "year": year,
                "month": month,
                "month_name": month_name,
                "income": income,
                "expenses": expenses,
                "net": net,
                "savings_rate": round(savings_rate, 1),
                "budget_status": budget_status,
                "budget_performance": round(budget_performance, 1) if budget_target > 0 else None,
                "transaction_count": monthly_summary.get("transaction_count", 0),
                "expenses_by_category": monthly_summary.get("expenses_by_category", {}),
                "insights": self._generate_monthly_insights(monthly_summary, user),
                "recommendations": self._generate_monthly_recommendations(monthly_summary, user)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating monthly report for user {user_id}: {str(e)}")
            return {"error": f"Failed to generate monthly report: {str(e)}"}
    
    def _generate_monthly_insights(self, monthly_summary: Dict[str, Any], user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights for monthly report
        
        Args:
            monthly_summary: Monthly transaction summary
            user: User profile
            
        Returns:
            List of insights
        """
        insights = []
        
        # Calculate basic metrics
        income = monthly_summary.get("income", 0)
        expenses = monthly_summary.get("expenses", 0)
        net = income - expenses
        expenses_by_category = monthly_summary.get("expenses_by_category", {})
        
        # Insight 1: Savings rate
        if income > 0:
            savings_rate = (net / income) * 100
            
            if savings_rate >= 20:
                insights.append({
                    "type": "positive",
                    "title": "Great savings rate",
                    "description": f"You saved {savings_rate:.1f}% of your income this month, which is above the recommended 20%."
                })
            elif savings_rate < 0:
                insights.append({
                    "type": "negative",
                    "title": "Negative savings",
                    "description": f"You spent ${abs(net):.2f} more than you earned this month."
                })
            elif savings_rate < 10:
                insights.append({
                    "type": "warning",
                    "title": "Low savings rate",
                    "description": f"Your savings rate of {savings_rate:.1f}% is below the recommended 20%."
                })
        
        # Insight 2: Largest expense category
        if expenses_by_category:
            largest_category = max(expenses_by_category.items(), key=lambda x: x[1])
            category_name = largest_category[0]
            category_amount = largest_category[1]
            
            if expenses > 0:
                category_percentage = (category_amount / expenses) * 100
                
                if category_percentage > 40 and category_name not in ["Housing", "Rent", "Mortgage"]:
                    insights.append({
                        "type": "warning",
                        "title": f"High {category_name} spending",
                        "description": f"You spent {category_percentage:.1f}% of your expenses on {category_name}, which may be higher than optimal."
                    })
                else:
                    insights.append({
                        "type": "neutral",
                        "title": f"Largest spending category",
                        "description": f"Your largest expense was {category_name} at ${category_amount:.2f} ({category_percentage:.1f}% of total expenses)."
                    })
        
        # Insight 3: Income change (if we had previous month data)
        # This would normally compare to previous periods
        
        return insights
    
    def _generate_monthly_recommendations(self, monthly_summary: Dict[str, Any], user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations for monthly report
        
        Args:
            monthly_summary: Monthly transaction summary
            user: User profile
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Calculate basic metrics
        income = monthly_summary.get("income", 0)
        expenses = monthly_summary.get("expenses", 0)
        net = income - expenses
        expenses_by_category = monthly_summary.get("expenses_by_category", {})
        
        # Recommendation 1: Savings
        if income > 0:
            savings_rate = (net / income) * 100
            
            if savings_rate < 20:
                recommendations.append({
                    "title": "Increase your savings rate",
                    "description": f"Aim to save at least 20% of your income. Currently you're at {savings_rate:.1f}%.",
                    "action": "Set up automatic transfers to your savings account on payday."
                })
        
        # Recommendation 2: Budget optimization
        if expenses_by_category:
            # Find potentially reducible categories
            reducible_categories = ["Dining", "Entertainment", "Shopping", "Subscription"]
            reducible_total = sum(expenses_by_category.get(cat, 0) for cat in reducible_categories)
            
            if reducible_total > 0 and reducible_total > 0.3 * expenses:
                recommendations.append({
                    "title": "Optimize discretionary spending",
                    "description": f"You spent ${reducible_total:.2f} on discretionary categories, which is {(reducible_total/expenses)*100:.1f}% of your expenses.",
                    "action": "Review your subscriptions and dining expenses for potential savings."
                })
        
        # Recommendation 3: Emergency fund
        emergency_fund_goal = next((g for g in user.get("financial_goals", []) if g.get("type") == "emergency_fund"), None)
        
        if not emergency_fund_goal and net > 0:
            recommendations.append({
                "title": "Start an emergency fund",
                "description": "Having 3-6 months of expenses saved for emergencies is essential for financial security.",
                "action": "Create an emergency fund goal and set up a high-yield savings account."
            })
        
        return recommendations