from fastapi import APIRouter, Depends, HTTPException, Response, Request
import uuid

from src.utils.roles import roles_required, get_token_from_cookie
from src.components.auth.controller import oauth2_scheme
from db_config.enums import UserRole
from db_config.db_connection import session
from src.components.categories.repository import CategotyRepository
from db_config.db_tables import Category
from src.components.categories.schemas import CategoryReq

repository = CategotyRepository(session)

ADMIN, USER = UserRole.admin, UserRole.user 

categories_router = APIRouter(
    prefix="/categories",
    tags=["Categories"])

@categories_router.get("/")
async def get_all_categories():
    return repository.get_all_categories()

@categories_router.get("/{category_id}")
async def get_category_by_id(request: Request, category_id: str):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    return repository.get_category_by_id(category_id)

@categories_router.post("/")
async def create_category(request: Request, data: CategoryReq):
    print(data.model_dump())
    print(request.cookies.get("access_token"))
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    new_category = Category(id=str(uuid.uuid4()), **data.model_dump())
    return repository.create_category(new_category)

@categories_router.put("/{category_id}")
async def update_category(request: Request, updates: CategoryReq, category_id: str):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    category = repository.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return repository.update_category({"id": category_id, **updates.model_dump()})

@categories_router.delete("/{category_id}")
async def delete_category(request: Request, id: str):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    return repository.delete_category(id)