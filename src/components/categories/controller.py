from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import uuid

from src.utils.roles import roles_required
from src.components.auth.controller import oauth2_scheme
from db_config.enums import UserRole
from db_config.db_connection import session
from src.components.categories.repository import CategotyRepository
from db_config.db_tables import Category
from src.components.categories.schemas import CategoryReq

repository = CategotyRepository(session)

ADMIN, USER = UserRole.admin, UserRole.user

def admin_role_required(token: Annotated[str, Depends(oauth2_scheme)]):
    return roles_required([ADMIN], token)

categories_router = APIRouter(
    prefix="/categories",
    tags=["Categories"])

@categories_router.get("/")
async def get_all_categories():
    return repository.get_all_categories()

@categories_router.get("/{category_id}")
async def get_category_by_id(category_id: str, authorization: str = Depends(admin_role_required)):
    return repository.get_category_by_id(category_id)

@categories_router.post("/")
async def create_category(data: CategoryReq, authorization: str = Depends(admin_role_required)):
    new_category = Category(id=str(uuid.uuid4()), **data.model_dump())
    return repository.create_category(new_category)

@categories_router.put("/{category_id}")
async def update_category(updates: CategoryReq, category_id: str, authorization: str = Depends(admin_role_required)):
    category = repository.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return repository.update_category({"id": category_id, **updates.model_dump()})

@categories_router.delete("/{category_id}")
async def delete_category(id: str, authorization: str = Depends(admin_role_required)):
    return repository.delete_category(id)