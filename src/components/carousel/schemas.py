from pydantic import BaseModel, model_validator

class CarouselReq(BaseModel):
    id: str = None
    img_url: str
    slug: str = None

    @model_validator(mode='after')
    def check_img_url(self):
        if self.img_url is None or self.img_url.strip() == '':
            raise ValueError('IMAGE URL IS REQUIRED')
        return self
    
class CarouselRes(BaseModel):
    id: str
    img_url: str
    slug: str = None

    @model_validator(mode='after')
    def check_img_url(self):
        if self.img_url is None or self.img_url.strip() == '':
            raise ValueError('IMAGE URL IS REQUIRED')
        return self
    
    @model_validator(mode='after')
    def check_id(self):
        if self.id is None or self.id.strip() == '':
            raise ValueError('ID IS REQUIRED')
        return self
    
class CarouselCreateReq(BaseModel):
    img_url: str
    slug: str = None

    @model_validator(mode='after')
    def check_img_url(self):
        if self.img_url is None or self.img_url.strip() == '':
            raise ValueError('IMAGE URL IS REQUIRED')
        return self