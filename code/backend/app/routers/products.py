from fastapi import APIRouter, HTTPException, status
from app.models.schemas import Product
from app.utils.database import products
from typing import List

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: Product):
    # Convert to dict and save to database
    product_dict = product.dict()
    result = products.insert_one(product_dict)
    
    # Return the created product
    return {**product_dict, "product_id": str(result.inserted_id)}

@router.get("/", response_model=List[Product])
async def get_products():
    # Retrieve all products from the database
    all_products = list(products.find())
    return all_products

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = products.find_one({"product_id": product_id})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product