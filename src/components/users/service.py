from fastapi import HTTPException
from fastapi.responses import JSONResponse
from .schemas import UserUpdateReq, UserRegister, ResetPasswordReq
from db_config.db_tables import User, UserRole, ResetPasswordToken
from .repository import UserRepository
from pydantic import EmailStr
import uuid
from datetime import datetime, timedelta
from src.utils.email_handler import EmailHandler
from src.utils.password_hash import get_password_hash, verify_password 
from src.utils.jwt_handler import TokenHandler

class UserService():
    def __init__(self, session, user_repository: UserRepository, email_handler: EmailHandler, token_handler: TokenHandler, user_role: UserRole)-> None: 
        self.user_repository: UserRepository = user_repository(session)
        self.email_handler = email_handler
        self.token_handler = token_handler
        self.user_role = user_role

    def get_all_users(self):
        return self.user_repository.get_all_users()
    
    def get_user_by_confirmation_code(self, code):
        return self.user_repository.get_user_by_confirmation_code(code)

    def confirm_user(self, unconfirmed_user: User):      
        try:
            confirmed_user = {
                "role": self.user_role.user,
                "confirmation_code": 1
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Something went wrong confirming submition in service: {e}")
        return self.user_repository.update_user(unconfirmed_user.user_id, confirmed_user)
        # TODO: Review if userRole is UNCONFIRMED for a long time, to delete it so that it can't be used anymore...
    def create_register_submition(self, data: UserRegister):                
        email_handler = self.email_handler(data.email)
        email_handler.send_verification_email()
        try:
            user = User( 
                user_id = str(uuid.uuid4()),
                name = data.user_name,
                email = data.email,
                role = UserRole.unconfirmed,
                password_hash = get_password_hash(data.password),
                confirmation_code = email_handler.get_verification_code()
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Something went wrong creating register model in service: {e}")
        return self.user_repository.create_user(user)
        
    def forgot_password(self, email: EmailStr):
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
                expires_at = datetime.now() + timedelta(minutes=10),
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Couldn't create reset_passwor_token in /users/service: {e}")

        self.user_repository.save_reset_password_token(reset_password_token)
        return JSONResponse(status_code=200, content={"message": f'Email to "{email}" sent successfully.'})
        
    def reset_password(self, reset_password_req: ResetPasswordReq):
        token_exist: ResetPasswordToken = self.user_repository.get_reset_password_token(reset_password_req.token)
        if not token_exist:
            raise HTTPException(status_code=404, detail=f'Change password token for "{reset_password_req.email}" not found')
        elif token_exist.expires_at < datetime.now():
            raise HTTPException(status_code=404, detail=f'Token has expired')
        password_update = {
            "password_hash": get_password_hash(reset_password_req.password1)
            }
        return self.user_repository.update_user(token_exist.user_id, password_update)

    def get_user_by_id(self, user_id: str):
        return self.user_repository.get_user_by_id(user_id)

    def get_user_by_email(self, user_email: EmailStr): 
        return self.user_repository.get_user_by_email(user_email)

    def update_user(self, user_id: str, user_updates: UserUpdateReq):
        user: User = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
        verified_password = verify_password(user_updates.current_password, user.password_hash)
        if not verified_password:
            raise HTTPException(status_code=400, detail="Invalid password")
        try:
            updated_user = {
                "name": user_updates.name,
                "email": user_updates.email,
                "password_hash": get_password_hash(user_updates.new_password)
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Something went wrong updating user in service: {e}")
        return self.user_repository.update_user(user.user_id, updated_user)           

    def delete_user(self, user_id: str):
        return self.user_repository.delete_user(user_id)