"""
Catalog Module Routes - Product Management
=========================================

FastAPI router for product catalog management using modular service architecture.
Handles millions of products with high performance and scalability.
"""

from fastapi import APIRouter, HTTPException, Request, Query, Path, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging
import os
from pathlib import Path

# Import our modular services
from .services.product_service import ProductService
from .services.category_service import CategoryService
from .services.search_service import SearchService
from .services.media_service import MediaService

# Import shared services and database managers
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.product_repository import ProductRepository
from src.shared.repositories.category_repository import CategoryRepository

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["catalog"])

# Template setup
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize shared services
data_dir = Path("data")
db_path = data_dir / "ecommerce_database.db"
connection_manager = DatabaseConnectionManager(db_path)
db_manager = BaseDatabaseManager(connection_manager)

# Create repository instances
product_repo = ProductRepository(db_manager)
category_repo = CategoryRepository(db_manager)

# Create service instances
product_service = ProductService(db_manager, product_repo)
category_service = CategoryService(db_manager, category_repo)
search_service = SearchService(db_manager, product_repo)
media_service = MediaService()

# Pydantic models
class ProductCreate(BaseModel):
    name: str
    description: str
    sku: str
    price: float
    category_id: str
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    attributes: Optional[Dict[str, Any]] = None
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    attributes: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    slug: str
    is_active: bool = True

# Page routes
@router.get("/", response_class=HTMLResponse)
async def catalog_dashboard(request: Request):
    """Catalog management dashboard."""
    try:
        # Get catalog statistics
        stats = await product_service.get_catalog_statistics()
        
        return templates.TemplateResponse(
            "catalog/dashboard.html",
            {
                "request": request,
                "stats": stats,
                "active_tab": "dashboard"
            }
        )
    except Exception as e:
        logger.error(f"Error loading catalog dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/products", response_class=HTMLResponse)
async def products_page(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("name", regex="^(name|price|created_at|updated_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$")
):
    """Products listing page with search and filtering."""
    try:
        # Get products with pagination and filtering
        products_data = await product_service.get_products_paginated(
            page=page,
            limit=limit,
            category_id=category,
            search_term=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get categories for filter dropdown
        categories = await category_service.get_all_categories()
        
        return templates.TemplateResponse(
            "catalog/products.html",
            {
                "request": request,
                "products": products_data["products"],
                "pagination": products_data["pagination"],
                "categories": categories,
                "filters": {
                    "category": category,
                    "search": search,
                    "sort_by": sort_by,
                    "sort_order": sort_order
                },
                "active_tab": "products"
            }
        )
    except Exception as e:
        logger.error(f"Error loading products page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request):
    """Categories management page."""
    try:
        # Get category tree
        categories = await category_service.get_category_tree()
        
        return templates.TemplateResponse(
            "catalog/categories.html",
            {
                "request": request,
                "categories": categories,
                "active_tab": "categories"
            }
        )
    except Exception as e:
        logger.error(f"Error loading categories page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# API routes
@router.get("/api/products")
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("name", regex="^(name|price|created_at|updated_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$")
):
    """Get products with pagination and filtering."""
    try:
        products_data = await product_service.get_products_paginated(
            page=page,
            limit=limit,
            category_id=category,
            search_term=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return products_data
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/products/{product_id}")
async def get_product(product_id: str = Path(...)):
    """Get product by ID."""
    try:
        product = await product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/products")
async def create_product(product_data: ProductCreate):
    """Create a new product."""
    try:
        product = await product_service.create_product(product_data.dict())
        return {"message": "Product created successfully", "product": product}
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/api/products/{product_id}")
async def update_product(
    product_id: str = Path(...),
    product_data: ProductUpdate = None
):
    """Update an existing product."""
    try:
        product = await product_service.update_product(
            product_id, 
            product_data.dict(exclude_unset=True)
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product updated successfully", "product": product}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api/products/{product_id}")
async def delete_product(product_id: str = Path(...)):
    """Delete a product."""
    try:
        success = await product_service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/categories")
async def get_categories():
    """Get all categories."""
    try:
        categories = await category_service.get_all_categories()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/categories/{category_id}")
async def get_category(category_id: str = Path(...)):
    """Get category by ID."""
    try:
        category = await category_service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category {category_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/categories")
async def create_category(category_data: CategoryCreate):
    """Create a new category."""
    try:
        category = await category_service.create_category(category_data.dict())
        return {"message": "Category created successfully", "category": category}
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/search")
async def search_products(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("relevance", regex="^(relevance|name|price|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """Search products with advanced filtering."""
    try:
        search_results = await search_service.search_products(
            query=q,
            page=page,
            limit=limit,
            category_id=category,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return search_results
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/products/{product_id}/variants")
async def get_product_variants(product_id: str = Path(...)):
    """Get product variants."""
    try:
        variants = await product_service.get_product_variants(product_id)
        return variants
    except Exception as e:
        logger.error(f"Error getting product variants {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/products/{product_id}/media")
async def get_product_media(product_id: str = Path(...)):
    """Get product media (images, videos)."""
    try:
        media = await media_service.get_product_media(product_id)
        return media
    except Exception as e:
        logger.error(f"Error getting product media {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 