from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.database import test_connection
from app.utils.mock_data import populate_mock_data
from app.routers import users, products, recommendations, sentiment
from app.routers import auth
from app.routers import dashboard
# from app.routers import chat
from app.routers import transactions
from app.routers import insights
from app.routers import transaction_intelligence
from app.routers import enhanced_recommendations
from app.routers import enhanced_chat


app = FastAPI(
    title="FinPersona AI API",
    description="Hyper-personalized banking recommendation system",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(recommendations.router)
app.include_router(sentiment.router)
app.include_router(dashboard.router)
# app.include_router(chat.router)
app.include_router(transactions.router)
app.include_router(insights.router)
app.include_router(transaction_intelligence.router)
app.include_router(enhanced_recommendations.router)
app.include_router(enhanced_chat.router)

@app.on_event("startup")
async def startup_event():
    # Test database connection
    if not test_connection():
        print("WARNING: Database connection failed. Some features may not work correctly.")
    
    # Populate mock data on startup
    try:
        await populate_mock_data()
        print("Mock data populated successfully")
    except Exception as e:
        print(f"Error populating mock data: {e}")

@app.get("/")
async def root():
    return {
        "message": "Welcome to FinPersona AI API",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    db_status = "connected" if test_connection() else "disconnected"
    return {
        "status": "healthy",
        "database": db_status
    }