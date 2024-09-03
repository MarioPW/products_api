from fastapi import HTTPException, Request
from src.utils.jwt_handler import TokenHandler
from src.components.users.repository import UserRepository
from db_config.db_connection import session

user_repository = UserRepository(session)

def roles_required(allowed_roles:list, token=None, code=None) -> None:
    user = None
    if token:
        decoded_user = TokenHandler.verify_token(token)
        if decoded_user:
            user = user_repository.get_user_by_id(decoded_user["user_id"])
    elif code:
        user = user_repository.get_user_by_confirmation_code(code)    
    if user is None or user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Access denied")

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token