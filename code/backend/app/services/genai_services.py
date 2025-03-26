from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime
# import google.generativeai as genai
# from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google import genai

# Configure API key
API_KEY = os.getenv("GENAI_API_KEY")
# genai.configure(api_key = API_KEY)

class GenAIService:
    """
    Centralized service for interacting with GenAI models.
    This class handles all GenAI model interactions throughout the application.
    """
    
    def __init__(self):
        """Initialize the GenAI service with model configuration"""
        # self.models = genai.list_models()
        # Use a suitable text model from available models
        # Usually this will be a model with "gemini" in the name
        self.model_name = "gemini-pro"

    async def generate_financial_advice(self, 
                                  user_profile: Dict[str, Any], 
                                  user_query: str,
                                  transaction_history: Optional[List[Dict[str, Any]]] = None,
                                  chat_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate personalized financial advice based on user's profile and query
        
        Args:
            user_profile: User data including financial information
            user_query: The question or request from the user
            transaction_history: Optional list of recent transactions
            chat_history: Optional list of previous chat messages for context
            
        Returns:
            str: AI-generated response
        """
        # Create a system prompt with financial domain knowledge
        system_prompt = """
        You are an advanced AI financial advisor specializing in personal finance.
        Provide helpful, accurate, and personalized financial advice based on the user's profile and transaction history.
        Focus on actionable insights and clear explanations. Be conversational but professional.
        Base your advice only on the information provided in the user's profile and transaction history.
        If you can't provide specific advice with the given information, explain what additional information would be helpful.
        """
        
        # Format user profile information for the prompt
        profile_summary = f"""
        User Profile:
        - Name: {user_profile.get('name', 'User')}
        - Age: {user_profile.get('profile', {}).get('age', 'Unknown')}
        - Risk Profile: {user_profile.get('financial_profile', {}).get('risk_profile', 'Unknown')}
        - Financial Health: {user_profile.get('financial_profile', {}).get('financial_health', 'Unknown')}
        - Current Balance: ${user_profile.get('financial_profile', {}).get('balance', 0):,.2f}
        - Monthly Income: ${user_profile.get('financial_profile', {}).get('monthly_income', 0):,.2f}
        - Monthly Expenses: ${user_profile.get('financial_profile', {}).get('monthly_expenses', 0):,.2f}
        - Credit Score: {user_profile.get('financial_profile', {}).get('credit_score', 'Unknown')}
        """
        
        # Format transaction data if provided
        transaction_summary = ""
        if transaction_history:
            # Summarize the most recent transactions
            recent_txns = transaction_history[:10]  # Last 10 transactions
            transaction_summary = "Recent Transactions:\n"
            
            for txn in recent_txns:
                date = txn.get('timestamp', datetime.now()).strftime("%Y-%m-%d") if isinstance(txn.get('timestamp'), datetime) else str(txn.get('timestamp', 'Unknown Date'))
                amount = txn.get('amount', 0)
                category = txn.get('category', 'Uncategorized')
                merchant = txn.get('merchant', 'Unknown')
                
                transaction_summary += f"- {date}: ${amount:,.2f} at {merchant} ({category})\n"
        
        # Format previous chat messages if provided
        chat_context = ""
        if chat_history and len(chat_history) > 0:
            chat_context = "Previous conversation:\n"
            for msg in chat_history[-5:]:  # Last 5 messages for context
                sender = "You" if msg.get('sender') == 'assistant' else "User"
                chat_context += f"{sender}: {msg.get('text', '')}\n"
        
        # Combine all context for the prompt
        full_prompt = f"{system_prompt}\n\n{profile_summary}\n\n{transaction_summary}\n\n{chat_context}\n\nUser Question: {user_query}\n\nYour response in less than 50 words:"
        
        # Generate response from GenAI model
        # response = self.model.generate_content(full_prompt)
        client = genai.Client(api_key = API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt)
        print(response.candidates[0].content.parts[0].text)
        return response.candidates[0].content.parts[0].text;

    
    async def generate_product_recommendation(self, 
                                       user_profile: Dict[str, Any], 
                                       product: Dict[str, Any],
                                       transaction_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a personalized product recommendation explanation
        
        Args:
            user_profile: User data
            product: Product details
            transaction_history: Optional user transaction history
            
        Returns:
            Dict containing recommendation text and score
        """
        system_prompt = """
        You are an AI specializing in personalized financial product recommendations.
        Analyze the user profile and product information to create a personalized recommendation.
        Explain clearly and specifically why this product would benefit this particular user based on their financial situation.
        Focus on concrete benefits and how the product addresses their specific needs and goals.
        """
        
        # Format user profile information
        profile_summary = f"""
        User Profile:
        - Age: {user_profile.get('profile', {}).get('age', 'Unknown')}
        - Income: {user_profile.get('financial_profile', {}).get('monthly_income', 0):,.2f}
        - Risk Profile: {user_profile.get('financial_profile', {}).get('risk_profile', 'Unknown')}
        - Financial Goals: {', '.join(goal.get('name', '') for goal in user_profile.get('financial_goals', []))}
        - Credit Score: {user_profile.get('financial_profile', {}).get('credit_score', 'Unknown')}
        """
        
        # Format product information
        product_summary = f"""
        Product Information:
        - Name: {product.get('name', 'Unknown')}
        - Category: {product.get('category', 'Unknown')}
        - Description: {product.get('description', 'No description')}
        - Features: {', '.join(product.get('features', []))}
        """
        
        # Add transaction summary if available
        transaction_info = ""
        if transaction_history:
            # Calculate average spending by category
            categories = {}
            for txn in transaction_history:
                category = txn.get('category', 'Other')
                amount = abs(txn.get('amount', 0)) if txn.get('amount', 0) < 0 else 0  # Only count expenses
                categories[category] = categories.get(category, 0) + amount
            
            # Format the spending summary
            transaction_info = "Spending Pattern:\n"
            for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                transaction_info += f"- {category}: ${amount:,.2f}\n"
        
        # Combine contexts
        full_prompt = f"{system_prompt}\n\n{profile_summary}\n\n{product_summary}\n\n{transaction_info}\n\nGenerate a personalized recommendation explanation:"
        
        # Generate recommendation text
        # response = self.model.generate_content(full_prompt)
        client = genai.Client(api_key = API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt)
        # print(response)
        # Generate a match score based on the user profile and product
        score_prompt = f"""
        Based on the following user profile and product information, calculate a match score from 0-100.
        Higher scores mean better match. Only return a number.
        
        {profile_summary}
        
        {product_summary}
        
        Match Score (0-100):
        """
        score_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=score_prompt)
        # score_response = self.model.generate_content()
        # print(score_response)
        
        try:
            # Extract numeric score from response
            score_text = score_response.text.strip()
            score = int(''.join(c for c in score_text if c.isdigit()))
            # Ensure score is within 0-100 range
            score = max(0, min(score, 100))
        except:
            # Default score if parsing fails
            score = 75
        
        return {
            "recommendation_text": response.text.strip(),
            "score": score
        }
    
    async def analyze_sentiment(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze financial sentiment based on transaction history
        
        Args:
            transactions: List of user transactions
            
        Returns:
            Dict with sentiment analysis results
        """
        if not transactions:
            return {
                "overall_sentiment": "neutral",
                "confidence": 0.5,
                "financial_health": "stable",
                "explanation": "Not enough transaction data to analyze."
            }
        
        # Create a summary of transactions
        transaction_summary = ""
        for txn in transactions[:20]:  # Analyze up to 20 recent transactions
            date = txn.get('timestamp', datetime.now()).strftime("%Y-%m-%d") if isinstance(txn.get('timestamp'), datetime) else str(txn.get('timestamp', 'Unknown Date'))
            amount = txn.get('amount', 0)
            category = txn.get('category', 'Uncategorized')
            
            transaction_summary += f"- {date}: ${amount:,.2f} ({category})\n"
        
        prompt = f"""
        Analyze the following transaction history and determine the financial sentiment.
        Categorize the overall sentiment as "positive", "neutral", or "negative".
        Assess financial health as "excellent", "good", "stable", "stressed", or "critical".
        
        Transaction History:
        {transaction_summary}
        
        Provide your analysis in JSON format with these fields:
        - overall_sentiment: The sentiment category (positive/neutral/negative)
        - confidence: Your confidence in this assessment (0.0-1.0)
        - financial_health: The financial health category
        - explanation: A brief explanation of your assessment
        
        JSON Response:
        """
        
        # response = self.model.generate_content(prompt)
        client = genai.Client(api_key = API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt)
        print(response)
        # Parse the JSON response
        try:
            # Try to extract JSON from the response
            text = response.text
            # Find JSON content between triple backticks if present
            if "```json" in text and "```" in text.split("```json")[1]:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text and "```" in text.split("```")[1]:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                json_str = text.strip()
                
            sentiment_data = json.loads(json_str)
            
            # Ensure required fields are present
            required_fields = ["overall_sentiment", "confidence", "financial_health", "explanation"]
            for field in required_fields:
                if field not in sentiment_data:
                    sentiment_data[field] = "unknown" if field != "confidence" else 0.5
            
            return sentiment_data
        except Exception as e:
            # Fallback response if JSON parsing fails
            return {
                "overall_sentiment": "neutral",
                "confidence": 0.5,
                "financial_health": "stable",
                "explanation": f"Could not analyze sentiment: {str(e)}"
            }
    
    async def detect_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect spending anomalies in transaction history
        
        Args:
            transactions: List of user transactions
            
        Returns:
            List of anomaly objects
        """
        if len(transactions) < 10:  # Not enough data
            return []
            
        # Prepare transactions summary by category
        categories = {}
        for txn in transactions:
            if txn.get('amount', 0) >= 0:  # Skip income
                continue
                
            date = txn.get('timestamp').strftime("%Y-%m-%d") if isinstance(txn.get('timestamp'), datetime) else str(txn.get('timestamp', ''))
            amount = abs(txn.get('amount', 0))
            category = txn.get('category', 'Other')
            merchant = txn.get('merchant', 'Unknown')
            
            if category not in categories:
                categories[category] = []
                
            categories[category].append({
                "date": date,
                "amount": amount,
                "merchant": merchant
            })
        
        # Format data for prompt
        category_summaries = ""
        for category, txns in categories.items():
            total = sum(t['amount'] for t in txns)
            avg = total / len(txns) if txns else 0
            category_summaries += f"\n{category}:\n"
            category_summaries += f"- Total: ${total:.2f}\n"
            category_summaries += f"- Average: ${avg:.2f}\n"
            category_summaries += f"- Transactions: {len(txns)}\n"
            category_summaries += "- Recent transactions:\n"
            
            for txn in sorted(txns, key=lambda x: x['date'], reverse=True)[:5]:
                category_summaries += f"  * {txn['date']}: ${txn['amount']:.2f} at {txn['merchant']}\n"
        
        prompt = f"""
        Analyze the following transaction data and identify any spending anomalies.
        Look for unusual spending patterns, significant increases in specific categories,
        or other financial behaviors that stand out.
        
        Transaction Data by Category:
        {category_summaries}
        
        Identify up to 3 specific anomalies or unusual patterns in JSON format:
        [
          {{
            "category": "Category name",
            "description": "Detailed description of the anomaly",
            "severity": "high/medium/low",
            "amount": numeric amount (if applicable)
          }}
        ]
        
        If no clear anomalies are detected, return an empty array [].
        
        Anomalies JSON:
        """
        
        # response = self.model.generate_content(prompt)
        client = genai.Client(api_key = API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt)
        print(response)
        
        try:
            # Try to extract JSON from the response
            text = response.text
            # Find JSON content between triple backticks if present
            if "```json" in text and "```" in text.split("```json")[1]:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text and "```" in text.split("```")[1]:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                json_str = text.strip()
                
            anomalies = json.loads(json_str)
            
            if not isinstance(anomalies, list):
                raise ValueError("Response is not a list of anomalies")
                
            # Add detection date
            for anomaly in anomalies:
                anomaly["detection_date"] = datetime.now()
                # Ensure all required fields exist
                if "category" not in anomaly:
                    anomaly["category"] = "Unknown"
                if "description" not in anomaly:
                    anomaly["description"] = "Unusual spending pattern detected"
                if "severity" not in anomaly:
                    anomaly["severity"] = "medium"
                
            return anomalies
            
        except Exception as e:
            # Return empty list if parsing fails
            return []
    
    async def generate_financial_insights(self, 
                                   user_profile: Dict[str, Any],
                                   transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate personalized financial insights based on user data
        
        Args:
            user_profile: User profile information
            transactions: Transaction history
            
        Returns:
            List of insight objects
        """
        if not transactions:
            return [{
                "category": "general",
                "description": "We'll provide personalized insights once you have transaction history.",
                "importance": "low"
            }]
            
        # Create transaction summary
        categories = {}
        total_spent = 0
        total_income = 0
        
        for txn in transactions:
            amount = txn.get('amount', 0)
            category = txn.get('category', 'Other')
            
            if amount < 0:  # Expense
                abs_amount = abs(amount)
                categories[category] = categories.get(category, 0) + abs_amount
                total_spent += abs_amount
            else:  # Income
                total_income += amount
        
        # Format category spending
        spending_summary = "\n".join([
            f"- {category}: ${amount:.2f} ({(amount/total_spent*100):.1f}%)"
            for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:8]
        ])
        
        # Extract user financial goals
        goals_summary = "\n".join([
            f"- {goal.get('name', 'Goal')}: ${goal.get('target_amount', 0):.2f} (Current: ${goal.get('current_amount', 0):.2f})"
            for goal in user_profile.get('financial_goals', [])
        ])
        
        prompt = f"""
        As a financial advisor, analyze this user's profile and transaction data to generate 3-5 key financial insights.
        Focus on actionable, specific insights that would be most valuable to the user.
        
        User Profile:
        - Risk Profile: {user_profile.get('financial_profile', {}).get('risk_profile', 'Unknown')}
        - Income: ${user_profile.get('financial_profile', {}).get('monthly_income', 0):.2f}/month
        - Expenses: ${user_profile.get('financial_profile', {}).get('monthly_expenses', 0):.2f}/month
        - Credit Score: {user_profile.get('financial_profile', {}).get('credit_score', 'Unknown')}
        
        Spending by Category:
        {spending_summary}
        
        Financial Goals:
        {goals_summary}
        
        Transaction Summary:
        - Total Income: ${total_income:.2f}
        - Total Expenses: ${total_spent:.2f}
        - Net: ${total_income - total_spent:.2f}
        
        Generate 3-5 specific, actionable financial insights as a JSON array where each insight has:
        - category: The category (spending, saving, investment, debt, etc.)
        - description: The detailed insight description
        - importance: Priority level (high, medium, low)
        
        Insights JSON:
        """
        
        # response = self.model.generate_content(prompt)
        client = genai.Client(api_key = API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt)
        print(response)
        
        try:
            # Try to extract JSON from the response
            text = response.text
            # Find JSON content between triple backticks if present
            if "```json" in text and "```" in text.split("```json")[1]:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text and "```" in text.split("```")[1]:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                json_str = text.strip()
                
            insights = json.loads(json_str)
            
            if not isinstance(insights, list):
                raise ValueError("Response is not a list of insights")
                
            return insights
                
        except Exception as e:
            # Fallback if parsing fails
            return [{
                "category": "general",
                "description": "Based on your spending patterns, you may have opportunities to optimize your budget.",
                "importance": "medium"
            }]
    
    async def generate_predictive_expenses(self, 
                                    transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict upcoming expenses based on transaction history
        
        Args:
            transactions: List of user transactions
            
        Returns:
            List of predicted expense objects
        """
        if not transactions or len(transactions) < 10:
            return []
            
        # Identify recurring transactions
        date_amounts = {}
        
        for txn in transactions:
            if txn.get('amount', 0) >= 0:  # Skip income
                continue
                
            timestamp = txn.get('timestamp')
            if not timestamp:
                continue
                
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    continue
                    
            day = timestamp.day
            amount = abs(txn.get('amount', 0))
            category = txn.get('category', 'Other')
            description = txn.get('description', txn.get('merchant', 'Unknown'))
            
            key = f"{category}_{description}"
            if key not in date_amounts:
                date_amounts[key] = []
                
            date_amounts[key].append({
                "day": day,
                "amount": amount,
                "date": timestamp
            })
        
        # Prepare data for the GenAI prompt
        recurring_data = ""
        for key, transactions in date_amounts.items():
            if len(transactions) < 2:
                continue
                
            category, description = key.split('_', 1)
            amounts = [t['amount'] for t in transactions]
            days = [t['day'] for t in transactions]
            dates = [t['date'].strftime("%Y-%m-%d") for t in transactions]
            
            recurring_data += f"\n{description} ({category}):\n"
            recurring_data += f"- Amounts: {', '.join(['${:.2f}'.format(a) for a in amounts])}\n"
            recurring_data += f"- Days of month: {', '.join([str(d) for d in days])}\n"
            recurring_data += f"- Dates: {', '.join(dates)}\n"
            recurring_data += f"- Occurrences: {len(transactions)}\n"
            
        now = datetime.now()
        
        prompt = f"""
        Analyze these potentially recurring transactions and predict upcoming expenses for the next 30 days.
        Today's date is {now.strftime("%Y-%m-%d")}.
        
        Recurring Transaction Patterns:
        {recurring_data}
        
        Generate predictions in JSON format with the following fields for each prediction:
        - description: Brief description of the expense
        - category: Expense category
        - amount: Predicted amount
        - due_date: Predicted date in YYYY-MM-DD format
        - confidence: Confidence score (0.0-1.0)
        - is_recurring: Boolean indicating if it's a recurring expense
        
        Only include predictions with reasonable confidence (>0.6).
        
        Predictions JSON Array:
        """
        
        # response = self.model.generate_content(prompt)
        client = genai.Client(api_key = API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt)
        print(response)
        
        try:
            # Try to extract JSON from the response
            text = response.text
            # Find JSON content between triple backticks if present
            if "```json" in text and "```" in text.split("```json")[1]:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text and "```" in text.split("```")[1]:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                json_str = text.strip()
                
            predictions = json.loads(json_str)
            
            if not isinstance(predictions, list):
                raise ValueError("Response is not a list of predictions")
                
            # Process dates and add expense_id
            processed_predictions = []
            for i, pred in enumerate(predictions):
                if "description" not in pred or "amount" not in pred or "due_date" not in pred:
                    continue
                    
                # Convert date string to datetime
                try:
                    due_date = datetime.fromisoformat(pred["due_date"])
                except:
                    # Skip predictions with invalid dates
                    continue
                    
                prediction = {
                    "expense_id": f"exp{i+1}_{now.strftime('%Y%m%d')}",
                    "description": pred["description"],
                    "amount": float(pred["amount"]),
                    "due_date": due_date,
                    "category": pred.get("category", "Other"),
                    "confidence": float(pred.get("confidence", 0.7)),
                    "is_recurring": bool(pred.get("is_recurring", True))
                }
                
                processed_predictions.append(prediction)
                
            return processed_predictions
            
        except Exception as e:
            # Return empty list if parsing fails
            return []