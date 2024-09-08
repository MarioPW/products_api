from fastapi import APIRouter, Depends
from typing import Annotated

from db_config.db_connection import session
from src.components.auth.controller import oauth2_scheme
from src.components.users.service import UserService
from src.components.users.schemas import User, UserUpdateReq
from src.utils.roles import roles_required
from src.utils.email_handler import EmailHandler
from src.utils.jwt_handler import TokenHandler
from db_config.enums import UserRole
from .repository import UserRepository
from src.utils.jwt_handler import TokenHandler

def only_admin(token: Annotated[str, Depends(oauth2_scheme)]):
    return roles_required([ADMIN], token)

def user_admin(token: Annotated[str, Depends(oauth2_scheme)]):
    return roles_required([ADMIN, USER], token)

users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    )

user_service = UserService(session, UserRepository, EmailHandler, TokenHandler, UserRole)
ADMIN, USER, UNCONFIRMED = UserRole.admin, UserRole.user, UserRole.unconfirmed
   
@users_router.get("/", response_model=list[User])
def get_all_users(authorization: str = Depends(only_admin)) -> list:
    return user_service.get_all_users()

@users_router.get("/user_id/{user_id}", response_model=User)
def get_user_by_id(user_id: str, authorization: str = Depends(only_admin)):
    return user_service.get_user_by_id(user_id)

@users_router.put("/{updates}")
def update_user(user_updates: UserUpdateReq, authorization: str = Depends(user_admin)):
    user_id = TokenHandler.verify_token(authorization)["user_id"]
    return user_service.update_user(user_id, user_updates)

@users_router.delete("/{del_user_id}")
def delete_user(del_user_id: str, authorization: str = Depends(user_admin)):
    if authorization["role"] == "user":
        del_user_id = authorization["user_id"]
    return user_service.delete_user(del_user_id)

@users_router.get("/check_authorization")
def check_authorization(authorization: str = Depends(only_admin)):
    return {"status_code": 200, "message": "Authorized"}