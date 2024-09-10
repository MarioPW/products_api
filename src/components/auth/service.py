
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

from src.components.users.repository import UserRepository
from src.utils.jwt_handler import TokenHandler
from db_config.db_tables import User, UserRole, ResetPasswordToken
import uuid
from src.utils.password_hash import get_password_hash, verify_password
from .repository import AuthRepository

class AuthService:
    def __init__(self, session, auth_repository, user_repository, email_handler, token_handler):
        self.auth_repository: AuthRepository = auth_repository(session)
        self.user_repository: UserRepository = user_repository(session)
        self.email_handler = email_handler
        self.token_handler: TokenHandler = token_handler
    def pre_register(self, data):
        email_handler = self.email_handler(data.email)
        email_handler.send_verification_email()
        try:
            user = User( 
                user_id = str(uuid.uuid4()),
                name = data.user_name,
                email = data.email,
                role = UserRole.unconfirmed,
                password_hash = get_password_hash(data.password),
                confirmation_code = email_handler.get_verification_code(),
                 )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Something went wrong creating register model in service: {e}")
        return self.auth_repository.create_pre_register(user)

    def confirm_register(self, confirmation_code:int):
        user = self.user_repository.get_user_by_confirmation_code(confirmation_code)
        if not user:
            return HTTPException(status_code=404, detail="User not found")
        updates = {
            "role": UserRole.user,
            "confirmation_code": 0
            }
        return self.user_repository.update_user(user.user_id, updates)

    def login(self, form_data):
        user_db = self.user_repository.get_user_by_email(form_data.username)
        if not user_db:
            raise HTTPException(status_code=401, detail=f"User {form_data.username} not authenticated")
        if user_db.role != UserRole.admin and user_db.role != UserRole.user:
            raise HTTPException(status_code=403, detail=f"Forbidden: Not authorized in UserService.login()")
        verified_password = verify_password(form_data.password, user_db.password_hash)
        if not verified_password:
            raise HTTPException(status_code=400, detail="Incorrect User or Password")
        try:
            user_data_token = {
                "user_id": user_db.user_id,
                "name": user_db.name,
                "email": user_db.email,
                "role": user_db.role
                }
            return {
                    "access_token": self.token_handler.create_access_token(user_data_token),
                    "token_type": "bearer"
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating user token: {e}")

    def forgot_password(self, email):
        user_exist = self.user_repository.get_user_by_email(email)
        if not user_exist:
            raise HTTPException(status_code=404, detail=f'User "{email}" not found')
        
        update_attempts_to_change_password = {"attempts_to_change_password": user_exist.attempts_to_change_password + 1}
        self.user_repository.update_user(user_exist.user_id, update_attempts_to_change_password)

        email_handler = self.email_handler(email)
        email_handler.send_change_password_email()
        reset_password_code = email_handler.get_reset_password_code()
        try: 
            reset_password_token = ResetPasswordToken(
                user_id = user_exist.user_id,
                token = reset_password_code,
                created_at = datetime.now(),
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Couldn't create reset_passwor_token in auth/service: {e}")
        
        self.auth_repository.save_reset_password_token(reset_password_token)
        return JSONResponse(status_code=200, content={"message": f'Email to "{email}" sent successfully.'})

    def reset_password(self, reset_password_req):
        reset_password_token_db = self.auth_repository.get_reset_password_token(reset_password_req.token)
        if not reset_password_token_db:
            raise HTTPException(status_code=404, detail=f'Reset password token for {reset_password_req.email} not found')
        if reset_password_token_db.created_at < datetime.now() - timedelta(minutes=10):
            raise HTTPException(status_code=404, detail='Reset password token expired')
        
        update_user = {"password_hash": get_password_hash(reset_password_req.password1)}
        self.user_repository.update_user(reset_password_token_db.user_id, update_user)
        return JSONResponse(status_code=200, content={"message": f'Password reset successfully'})