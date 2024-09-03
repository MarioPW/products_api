from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(password, password_hash):
    return bcrypt_context.verify(password, password_hash)

# password = get_password_hash("password")
# print(password)