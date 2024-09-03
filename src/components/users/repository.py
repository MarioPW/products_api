from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import  Dict, List
from pydantic import EmailStr
from db_config.db_tables import User, ResetPasswordToken

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_users(self):
        try:
            all_users: List = self.db.query(User).all()
            return all_users
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting all users in repository: {e}")
    
    def get_user_by_confirmation_code(self, code):
        try:
            user = self.db.query(User).filter(User.confirmation_code == code).first()
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=404, detail=f"User with code {code} not found in repository: {e}")
        
    def create_user(self, user:User):
        try:
            self.db.add(user)
            self.db.commit()        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating user in repository: {e}")
        return JSONResponse(status_code=200, content={"message": f"User {user.email} created successfully."})
    
    def get_user_by_id(self,user_id:str):
        try:
            return self.db.query(User).filter(User.user_id==user_id).first()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"User not found: {e}")

    def get_user_by_email(self, email:EmailStr):
        try:
            return self.db.query(User).filter(User.email==email).first()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"User with email {email} not found: {e}")

    def update_user(self, id: str, data: Dict):
        try:
            self.db.query(User).filter(User.user_id == id).update(data)
            self.db.commit()
            updated_user: User = self.get_user_by_id(id) 
            if updated_user:
                return JSONResponse(status_code=200, content={"message": f"User {updated_user.name} updated successfully."})
            else:
                raise HTTPException(status_code=404, detail=f"User with id {id} not found.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating user in repository: {e}")
    
    def save_reset_password_token(self, reset_password_token: ResetPasswordToken):
        try:
            self.db.add(reset_password_token)
            self.db.commit()
            self.db.close()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating reset_password_token in users/repository: {e}")
    
    def get_reset_password_token(self, token):
        try:
            return self.db.query(ResetPasswordToken).filter(ResetPasswordToken.token == str(token)).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting reset_password_token in users/repository: {e}")

    # SOFT DELETION
    def delete_user(self, id:str):
        try:
            user: User = self.get_user_by_id(id)            
            if not user:
                raise HTTPException(status_code=404, detail=f"User not found: {e}")
            # ToDo: Create table for soft deletion to register deletion date, user, etc.                 
            # user.role = UserRole.deleted
            # self.db.commit()
            self.db.query(User).filter(User.user_id==id).delete()        
            return JSONResponse (status_code=200, content={"message": f"User {user.name} deleted successfully."})

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")