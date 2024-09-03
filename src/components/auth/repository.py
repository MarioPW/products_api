from fastapi import HTTPException
from fastapi.responses import JSONResponse
from db_config.db_tables import User, UserRole, ResetPasswordToken

class AuthRepository:
    def __init__(self, db):
        self.sess = db
    
    def create_pre_register(self, user:User):
        try:
            self.sess.add(user)
            self.sess.commit()        
        except Exception as e:
            self.sess.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating user in repository: {e}")
        return JSONResponse(status_code=200, content={"message": f"User {user.email} created successfully."})
    
    def save_reset_password_token(self, reset_password_token: ResetPasswordToken):
        try:
            self.sess.add(reset_password_token)
            self.sess.commit()
            self.sess.close()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating reset_password_token in users/repository: {e}")
    
    def get_reset_password_token(self, token):
        try:
            return self.sess.query(ResetPasswordToken).filter(ResetPasswordToken.token == str(token)).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting reset_password_token in users/repository: {e}")