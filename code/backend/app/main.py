from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.database import test_connection
from app.utils.mock_data import populate_mock_data
from app.routers import users, products, recommendations, sentiment

app = FastAPI(
    title="FinPersona AI API",
    description="Hyper-personalized banking recommendation system",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(recommendations.router)
app.include_router(sentiment.router)

@app.get("/insertMock")
async def startup_event():
    # Populate mock data on startup
    await populate_mock_data()

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