from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime
from uuid import UUID

class User(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    password_hash: str
    creation_date: datetime
    role: str
    confirmation_code: int
    attempts_to_change_password: int

class UserRegister(BaseModel):
    user_name: str
    email: EmailStr
    password: str
    password_confirm: str
    
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserRegister':
        password = self.password
        password_confirm = self.password_confirm
        if password != password_confirm:
            raise ValueError('PASSWORDS MUST MATCH')
        elif self.user_name is None or self.user_name == '':
            raise ValueError("Name is Required")
        elif self.email is None or self.email == '':
            raise ValueError("Email is Required")
        else:
            return self

class UserUpdateReq(BaseModel):
    name: str = None
    email: EmailStr = None
    current_password: str
    new_password: str = None

    @model_validator(mode='after')
    def check_passwords_match(self):
        current_password = self.current_password
        new_password = self.new_password
        if current_password is not None and new_password is not None and current_password == new_password:
            raise ValueError('Incorrect password')
        return new_password
    
class ConfirmationCode(BaseModel):
    code: int
    @model_validator(mode='after')
    def code_must_be_greater_than_one(self) -> 'ConfirmationCode':
        if self.code <= 999:
            raise ValueError("Code must have four digits.")
        return self.code
    
class ResetPasswordReq(BaseModel):
    token: UUID
    email: EmailStr
    password1: str
    password2: str
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserRegister':
        password1 = self.password1
        password2 = self.password2
        if password1 != password2:
            raise ValueError('PASSWORDS MUST MATCH')
        elif self.email is None or self.email == '':
            raise ValueError("Email is Required")
        else:
            return self

