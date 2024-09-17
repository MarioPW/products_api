from pydantic import BaseModel, model_validator, Field
from typing import List
from datetime import datetime

class ProductImage(BaseModel):
    id: str
    url: str
class SizeResponse(BaseModel):
    size: str
    id: int

class ProductReq(BaseModel):
    name: str
    price: float
    stock: int
    brand: str = None
    description: str
    category_name: str
    images: List[str] = None
    sizes: List[str] = None

    @model_validator(mode='after')
    def check_images_length(self):
        if len(self.images) > 5:
            raise ValueError("PRODUCTS CAN'T HAVE MORE THAN 5 IMAGES")
        return self
    @model_validator(mode='after')
    def check_category(self):
        if self.category_name is None or self.category_name == 'string':
            self.category_name = 'Todos'
        return self
class ProductUpdateRequest(BaseModel):
    id: str = None
    name: str = None
    price: float = None
    stock: int = None
    brand: str = None
    description: str = None
    category_name: str = None
    sizes: List[str] = None
    images: List[ProductImage] = Field(default_factory=list)
    @model_validator(mode='after')
    def check_category(self):
        if self.category_name is None or self.category_name == 'string':
            self.category_name = 'Todos'
        return self

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    stock: int
    brand: str
    description: str
    category_name: str
    sizes: List[SizeResponse] = None
    images: List[ProductImage]