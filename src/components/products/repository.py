from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from db_config.db_tables import Product, ProductImages, SizesLookup, product_sizes_association
import uuid

class ProductModel:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_products(self):
        try:
            return self.db.query(Product).options(joinedload(Product.sizes)).all()
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

    def get_product_sizes (self, id: str):
        try:
            return self.db.query(SizesLookup).filter(SizesLookup.id==id).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ERROR GETTING PRODUCT SIZES IN REPOSITORY: {e}")
        
    def create_product(self, new_product):
        try:
            self.db.add(new_product)
            self.db.commit()           
        except Exception as err:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f'Could not create product "{new_product.name}": {err}')
        return JSONResponse(status_code=200, content=f"Product {new_product.name} created successfully")
    
    def get_lookup_sizes(self, sizes):
        try:
            return self.db.query(SizesLookup).filter(SizesLookup.size.in_(sizes)).all()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"COULDN'T GET PRODUCT SIZES: {e}")

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
            raise HTTPException(status_code=404, detail=f"PRODUCT NOT FOUND IN REPOSITORY: {e}")
        
        for key, value in data.items():
            if key != "images" and key != "sizes":
                setattr(product, key, value)

        self.db.commit()
        self.db.refresh(product)
        return product
    
    def update_product_image(self, product_id: str, image: ProductImages):
        try:
            product = self.db.query(Product).filter(Product.id == product_id).one()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ERROR RETRIEVING PRODUCT: {e}")
        
        current_image = self.db.query(ProductImages).filter(ProductImages.id == image.id).first()
        
        if not current_image:
            raise HTTPException(status_code=404, detail="PRODUCT IMAGE REGISTER NOT FOUND")

        if current_image.url != image.url:
            current_image.url = image.url
            
            try:
                self.db.commit()  
                self.db.refresh(product)
            except Exception as e:
                self.db.rollback()
                raise HTTPException(status_code=500, detail=f"ERROR UPDATING PRODUCT IMAGE: {e}")
        
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

    def delete_product_image(self, id):
        to_delete = self.db.query(ProductImages).filter(ProductImages.id==id).first()
        if not to_delete:
            raise HTTPException(status_code=404, detail="Product image not found")
        try:
            self.db.delete(to_delete)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Couldn't delete product image: {e}")