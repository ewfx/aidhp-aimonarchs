import os
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

class LLMService:
    _instance = None
    model = None
    tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            # Load a lightweight model for the hackathon
            try:
                # Use a small model to fit in memory (3GB vs 30GB for larger models)
                model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
                cls._instance.tokenizer = AutoTokenizer.from_pretrained(model_name)
                cls._instance.model = AutoModelForCausalLM.from_pretrained(
                    model_name, 
                    torch_dtype=torch.float32,  # Use float16 if you have GPU
                    low_cpu_mem_usage=True
                )
                print(f"Loaded LLM model: {model_name}")
            except Exception as e:
                print(f"Error loading model: {e}")
                # Fallback to no model - will use template-based recommendations
                cls._instance.model = None
                cls._instance.tokenizer = None
        return cls._instance
    
    def generate_personalized_recommendation(self, user_profile, product, transaction_history=None):
        """
        Generate a personalized recommendation explanation using the LLM
        """
        if not self.model or not self.tokenizer:
            # Fallback to template-based recommendations if model isn't loaded
            return self._generate_template_recommendation(user_profile, product)
        
        # Prepare the prompt
        prompt = self._prepare_recommendation_prompt(user_profile, product, transaction_history)
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the recommendation part (strip the prompt)
        recommendation = response[len(prompt):].strip()
        
        return recommendation
    
    def _prepare_recommendation_prompt(self, user_profile, product, transaction_history=None):
        """
        Create a prompt for the LLM based on user and product
        """
        # Basic user information
        user_info = f"User: {user_profile['name']}, Age: {user_profile.get('age', 'Unknown')}, Income: {user_profile.get('income_bracket', 'Unknown')}, Risk profile: {user_profile.get('risk_profile', 'Unknown')}"
        
        # Financial goals
        goals = f"Financial goals: {', '.join(user_profile.get('financial_goals', ['Unknown']))}"
        
        # Product information
        product_info = f"Product: {product['name']}, Category: {product['category']}, Risk level: {product.get('risk_level', 'Unknown')}"
        
        # Transaction summary if available
        transactions_summary = ""
        if transaction_history:
            categories = {}
            for transaction in transaction_history:
                category = transaction.get('category', 'other')
                categories[category] = categories.get(category, 0) + transaction.get('amount', 0)
            
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
            transactions_summary = "Top spending categories: " + ", ".join([f"{cat} (${amt:.2f})" for cat, amt in top_categories])
        
        # Construct the full prompt
        prompt = f"""As a financial advisor, create a personalized recommendation for this banking product:

{user_info}
{goals}
{product_info}
{transactions_summary}

Write a brief, personalized recommendation explanation that explains why this product is a good match for the user's financial situation and goals:
"""
        
        return prompt
    
    def _generate_template_recommendation(self, user_profile, product):
        """
        Fallback method when LLM isn't available - uses templates
        """
        templates = [
            f"Based on your {user_profile.get('risk_profile', 'financial')} profile, our {product['name']} could help you achieve your {', '.join(user_profile.get('financial_goals', ['financial goals']))}.",
            f"Our {product['name']} aligns with your {user_profile.get('risk_profile', 'financial')} approach and could support your {user_profile.get('financial_goals', ['goals'])[0] if user_profile.get('financial_goals') else 'financial goals'}.",
            f"As someone with a {user_profile.get('income_bracket', 'steady')} income and {user_profile.get('risk_profile', 'balanced')} risk tolerance, you might benefit from our {product['name']}."
        ]
        
        import random
        return random.choice(templates)