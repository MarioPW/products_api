from enum import Enum as pyEnum

class UserRole(str, pyEnum):
    user = "user"
    admin = "admin"
    deleted = "deleted"
    guest = "guest"
    unconfirmed = "unconfirmed"