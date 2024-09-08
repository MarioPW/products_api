from fastapi import HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4

from sqlalchemy.orm import Session
from db_config.db_tables import CarouselImage

class CarouselRepository:
    def __init__(self, db:Session):
        self.db = db

    def get_carousel_imges(self):
        try:
            return self.db.query(CarouselImage).all()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error getting carousel: {e}")
    
    def get_carousel_image(self, id):
        try:
            return self.db.query(CarouselImage).filter(CarouselImage.id==id).first()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error gettin carousel image: {e}")

    def create_carousel_image(self, data):
        try:
            new_image = CarouselImage(id=str(uuid4()), **data)
            self.db.add(new_image)
            self.db.commit()
            return new_image
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating carousel image: {e}")
        
    def update_carousel_image(self, data):
        try:
           self.db.query(CarouselImage).filter(CarouselImage.id==data.id).update({
                CarouselImage.img_url: data.img_url,
                CarouselImage.slug: data.slug
           })
           self.db.commit()
           return JSONResponse(status_code=200, content={"msg": "Carousel image updated successfully"})
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating carousel image: {e}")

    def delete_carousel_image(self, id):
        try:
            self.db.query(CarouselImage).filter(CarouselImage.id == id).delete()
            self.db.commit()
            return JSONResponse(status_code=200, content={"msg": "Carousel image deleted successfully"})
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting image: {e}")