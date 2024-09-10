from pydantic import BaseModel, EmailStr, model_validator
from uuid import UUID


class Register(BaseModel):
    user_name: str
    email: EmailStr
    password: str
    password_confirm: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'Register':
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

class ResetPasswordReq(BaseModel):
    token: UUID
    password1: str
    password2: str
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'Register':
        password1 = self.password1
        password2 = self.password2
        if password1 != password2:
            raise ValueError('PASSWORDS MUST MATCH')
        return self

class ConfirmationCode(BaseModel):
    code: int
    @model_validator(mode='after')
    def code_must_be_greater_than_one(self) -> 'ConfirmationCode':
        if self.code not in range(1000, 9999):
            raise ValueError("Code must have four digits.")
        return self