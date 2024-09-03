from fastapi import APIRouter, HTTPException, Request

from db_config.db_connection import session
from src.components.users.service import UserService
from src.components.users.schemas import User, UserUpdateReq
from src.utils.roles import roles_required
from src.utils.email_handler import EmailHandler
from src.utils.jwt_handler import TokenHandler
from db_config.enums import UserRole
from .repository import UserRepository
from src.utils.jwt_handler import TokenHandler


users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    )

user_service = UserService(session, UserRepository, EmailHandler, TokenHandler, UserRole)
ADMIN, USER, UNCONFIRMED = UserRole.admin, UserRole.user, UserRole.unconfirmed
   
@users_router.get("/", response_model=list[User])
def get_all_users(request: Request) -> list:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    roles_required([ADMIN], token)
    return user_service.get_all_users()

@users_router.get("/user_id/{user_id}", response_model=User)
def get_user_by_id(request: Request, user_id: str):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    roles_required([ADMIN], token)
    return user_service.get_user_by_id(user_id)

@users_router.put("/{updates}")
def update_user(request: Request, user_updates: UserUpdateReq):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    roles_required([ADMIN, USER], token)
    user_id = TokenHandler.verify_token(token)["user_id"]
    return user_service.update_user(user_id, user_updates)

@users_router.delete("/{del_user_id}")
def delete_user(request: Request,del_user_id: str):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    roles_required([ADMIN, USER], token)
    user_credentials = TokenHandler.verify_token(token)
    if user_credentials["role"] != "admin" and user_credentials["user_id"] != del_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_service.delete_user(del_user_id)

@users_router.get("/check_authorization")
def check_authorization(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    verify_token = TokenHandler.verify_token(token)
    user = user_service.get_user_by_id(verify_token["user_id"])
    if not user or user.role != "admin":
        raise HTTPException(status_code=401, detail="Not authorized")
    return {"status_code": 200, "message": "Authorized"}