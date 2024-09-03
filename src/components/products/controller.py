from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from uuid import uuid4
from dotenv import load_dotenv
from os import getenv

from .repository import ProductModel
from src.components.products.schemas import ProductReq, ProductUpdateRequest, ProductResponse
from db_config.db_connection import session
from db_config.db_tables import Product, ProductImages
from src.utils.roles import roles_required
from db_config.enums import UserRole

load_dotenv()

ADMIN, USER = UserRole.admin, UserRole.user

products_router = APIRouter(
    prefix="/products",
    tags=["Products"],
)
products = ProductModel(session)

@products_router.get("/", response_model=list[ProductResponse])
async def get_all_products():
    all_products = await products.get_all_products()
    return all_products

@products_router.get("/{product_id}")
async def get_product_by_id(request: Request,id: str):
    token = request.cookies.get("access_token")
    roles_required([ADMIN, USER], token)
    return products.get_product_by_id(id)

@products_router.post("/")
async def create_product(request: Request, data:ProductReq):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    product_id = str(uuid4())
    new_product = Product(id=product_id, name=data.name, price=data.price, stock=data.stock, brand=data.brand, description=data.description, category_name=data.category_name)
    products.create_product(new_product)
    for image in data.images:
        image_register = ProductImages(id=str(uuid4()), url=image, product_id=product_id)
        products.save_product_image_url(image_register)
        print(image_register.product_id)  
    return JSONResponse(status_code=201, content={"message": "Product created successfully"})

@products_router.put("/{product_id}")
async def update_product(request: Request, id:str, updates:ProductUpdateRequest):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    product = products.get_product_by_id(updates.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return products.update_product(id, updates.model_dump())

@products_router.delete("/{product_id}")
async def delete_product(request: Request, id:str):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    return products.delete_product(id)

@products_router.get("/image_host/")
async def get_image_host(request: Request):
    token = request.cookies.get("access_token")
    print(token)
    roles_required([ADMIN], token)
    return getenv("IMAGES_SERVICE")