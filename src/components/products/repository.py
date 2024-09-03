from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db_config.db_tables import Product, ProductImages
import uuid

class ProductModel:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_products(self):
        try:
            return self.db.query(Product).all()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Not products found: {e}")
    def get_product_by_name(self, name: str):
        try:
            return self.db.query(Product).filter(Product.name==name).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting product by name in repository: {e}")
    
    def get_product_by_id(self, id: str):
        try:
            return self.db.query(Product).filter(Product.id==id).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting product by id in repository: {e}")

    def create_product(self, new_product):
        try:
            self.db.add(new_product)
            self.db.commit()           
        except Exception as err:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f'Could not create product "{new_product.name}": {err}')
        return JSONResponse(status_code=200, content=f"Product {new_product.name} created successfully")

    def save_product_image_url(self, image):
        try:
            self.db.add(image)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Couldn't save product image: {e}")
    
    def update_product(self, product_id: str, data: dict):
        try:
            product = self.db.query(Product).filter(Product.id == product_id).one()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Product not found in repository: {e}")
        
        for key, value in data.items():
            if key != "images":
                setattr(product, key, value)

        if "images" in data:
            self.db.query(ProductImages).filter(ProductImages.product_id == product_id).delete()

            for image_url in data["images"]:
                new_image = ProductImages(id=str(uuid.uuid4()), url=image_url, product_id=product_id)
                self.db.add(new_image)

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, id):
        to_delete = self.db.query(Product).filter(Product.id==id).first()
        if not to_delete:
            raise HTTPException(status_code=404, detail="Product not found")
        try:
            self.db.delete(to_delete)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Couldn't delete product: {e}")
        return JSONResponse(status_code=200, content=f"Product {to_delete.name} deleted successfully")