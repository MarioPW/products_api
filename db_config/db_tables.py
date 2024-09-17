from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from os import getenv
from passlib.context import CryptContext
import uuid

from .db_connection import Base, engine, session
from .enums import UserRole, ProductSizes


product_sizes_association = Table(
    'product_sizes_association',
    Base.metadata,
    Column('product_id', String, ForeignKey('products.id'), primary_key=True),
    Column('size_id', Integer, ForeignKey('product_sizes_lookup.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, unique=True)
    name = Column(String(40), nullable=False)
    email = Column(String(40), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    creation_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    role = Column(String, ForeignKey("user_roles_lookup.user_role"))
    confirmation_code = Column(Integer, nullable=False, default=0)
    attempts_to_change_password = Column(Integer, nullable=False, default=0)

    user_roles_lookup = relationship("UserRolesLookup", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, unique=True)
    name = Column(String(40), nullable=False, unique=True)
    price = Column(Float, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    brand = Column(String(40), default="Dalana Kids")
    description = Column(String(250), default="Dalana Kids")
    category_name = Column(String(40), ForeignKey("categories.name"), nullable=False, default="Todos")

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImages", back_populates="product", cascade="all, delete-orphan")
    sizes = relationship("SizesLookup", secondary=product_sizes_association, back_populates="product")

class SizesLookup(Base):
    __tablename__ = "product_sizes_lookup"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    size = Column(String, unique=True)

    product = relationship("Product", secondary=product_sizes_association, back_populates="sizes")

class ProductImages(Base):
    __tablename__ = "product_images"
    id = Column(String, primary_key=True, unique=True)
    url = Column(Text, nullable=False, default=getenv("CART_IMAGE"))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)

    product = relationship("Product", back_populates="images")

class UserRolesLookup(Base):
    __tablename__ = "user_roles_lookup"
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_role = Column(String, unique=True)

    user = relationship("User", back_populates="user_roles_lookup")
class ResetPasswordToken(Base):
    __tablename__ = 'reset_password_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255))
    token = Column(String(255))
    created_at = Column(DateTime)

class Category(Base):
    __tablename__ = "categories"
    id = Column(String, primary_key=True, unique=True)
    name = Column(String(40), nullable=False, unique=True, default="Todos los productos")
    color = Column(String(40), nullable=False, default="bg-blue-500")

    products = relationship("Product", back_populates="category")

class CarouselImage(Base):
    __tablename__ = "carousel"
    id = Column(String, primary_key=True, unique=True)
    img_url = Column(Text, nullable=False, default=getenv("CAROUSEL_IMAGE"))
    slug = Column(String(100), nullable=False, unique=True)

if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Migrations to database executed correctly in db_tables.py.")

    # ----------------------------------------------------------------------------------
    #                  INSERTION OF ENUMS DATA INTO LOOKUP TABLES:
    # ----------------------------------------------------------------------------------

    for role in UserRole:
        new_role = UserRolesLookup(user_role=role.name)
        session.add(new_role)
    
    for size in ProductSizes:
        new_size = SizesLookup(size=size.name)
        session.add(new_size)

    # ----------------------------------------------------------------------------------
    #                 INSERTION OF ADMIN USER DATA INTO USERS TABLE:
    # ----------------------------------------------------------------------------------

    bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    name = getenv("NAME")
    email = getenv("ADMIN_EMAIL")
    role = UserRole.admin.name

    admin_user_password = getenv("PASSWORD")
    admin_user_password_hash = bcrypt_context.hash(admin_user_password)
    admin_user = User(user_id = str(uuid.uuid4()), name=name, email=email, password_hash=admin_user_password_hash, role=role)
    
    session.add(admin_user)

    # ----------------------------------------------------------------------------------
    #            INSERTION OF DEFAULT CATEGORY "ALL (Todos)" INTO CATEGORIES TABLE:
    # ----------------------------------------------------------------------------------

    category = Category(id=str(uuid.uuid4()), name="Todos", color="blue-500")

    session.add(category)

    # ----------------------------------------------------------------------------------
    #             INSERTION OF DEFAULT CAROUSEL ITEMS INTO CAROUSEL TABLE:
    # ----------------------------------------------------------------------------------

    carousel = [CarouselImage(id=str(uuid.uuid4()), img_url=getenv("CAROUSEL_IMAGE"), slug=f"carousel{i}") for i in range(1, 6)]

    session.add_all(carousel)
    session.commit()
    session.close()