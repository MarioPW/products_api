from random import randint

def create_verification_code() -> int: 
    code_int = randint(1000, 9999)
    return code_int

# print(create_verification_code())