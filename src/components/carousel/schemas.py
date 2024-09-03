from pydantic import BaseModel, model_validator

class CarouselImage(BaseModel):
    img_url: str
    slug: str = None

    @model_validator(mode='after')
    def check_img_url(self):
        if self.img_url is None or self.img_url == '':
            raise ValueError('IMAGE URL IS REQUIRED')
        return self
    
class UpdateCarouselImage(BaseModel):
    id: str
    img_url: str
    slug: str = None

    @model_validator(mode='after')
    def check_img_url(self):
        if self.img_url is None or self.img_url == '':
            raise ValueError('IMAGE URL IS REQUIRED')
        return self
    
    @model_validator(mode='after')
    def check_id(self):
        if self.id is None or self.id == '':
            raise ValueError('ID IS REQUIRED')
        return self