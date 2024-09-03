from fastapi import APIRouter, Response, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import EmailStr

from .service import AuthService
from .schemas import Register, ResetPasswordReq, ConfirmationCode
from .repository import AuthRepository
from src.components.users.repository import UserRepository
from db_config.db_connection import session
from src.utils.email_handler import EmailHandler
from src.utils.jwt_handler import TokenHandler

auth_service = AuthService(session, AuthRepository, UserRepository, EmailHandler, TokenHandler)
auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth")

@auth_router.post("/register")
def pre_register(data: Register):
    return auth_service.pre_register(data)

@auth_router.post("/confirm")
def confirm_register(request:ConfirmationCode):
    return auth_service.confirm_register(request.code)

@auth_router.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    access_token = auth_service.login(data)
    response = Response()
    response.set_cookie(
        key="access_token",
        value=access_token["access_token"],
        httponly=True,
        secure=True,
        samesite="none"
    )
    return response

@auth_router.get("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        samesite="none",
        secure=True)
    return {"message": "Logout successful"}

@auth_router.post("/forgot_password")
def forgot_password(email: EmailStr):
    return auth_service.forgot_password(email)

@auth_router.post("/reset_password")
def reset_password(reset_password_req: ResetPasswordReq):
    return auth_service.reset_password(reset_password_req)