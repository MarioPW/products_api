from pydantic import BaseModel, model_validator, Field
from typing import List
from datetime import datetime

class ProductReq(BaseModel):
    name: str
    price: float
    stock: int
    brand: str = None
    description: str
    category_name: str
    images: List[str] = None
    size: str = None

    @model_validator(mode='after')
    def check_images_length(self):
        if len(self.images) > 5:
            raise ValueError("Products can't have more than 5 images")
        return self
    @model_validator(mode='after')
    def check_category(self):
        if self.category_name is None or self.category_name == 'string':
            self.category_name = 'Todos'
        return self
class ProductUpdateRequest(BaseModel):
    id: str
    name: str
    price: float
    stock: int
    brand: str
    description: str
    category_name: str
    size: str
    images: List[str] = Field(default_factory=list)
    @model_validator(mode='after')
    def check_category(self):
        if self.category_name is None or self.category_name == 'string':
            self.category_name = 'Todos'
        return self
class ProductImageResponse(BaseModel):
    id: str
    url: str

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    stock: int
    brand: str
    description: str
    category_name: str
    size: str
    images: List[ProductImageResponse]