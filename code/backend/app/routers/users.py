# app/routers/users.py
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import UserProfile
from app.db.user_operations import UserOperations

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserProfile):
    # Check if user with this email already exists
    existing_user = UserOperations.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Convert to dict and save to database
    user_dict = user.dict()
    user_id = UserOperations.create_user(user_dict)
    
    # Return the created user
    return {**user_dict, "user_id": user_id}

@router.get("/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    user = UserOperations.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserProfile)
async def update_user(user_id: str, user_update: UserProfile):
    # Check if user exists
    existing_user = UserOperations.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user data
    user_dict = user_update.dict()
    success = UserOperations.update_user(user_id, user_dict)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    # Return updated user
    return {**user_dict, "user_id": user_id}