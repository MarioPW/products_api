from pydantic import BaseModel, model_validator


class CategoryReq(BaseModel):
    name: str
    color: str = None

    @model_validator(mode='after')
    def check_color_exists(self):
        if self.color == '' or self.color == ' ' or self.color == 'string':
            self.color = 'bg-blue-500'
        elif self.name == None or self.name == '' or self.name == ' ' or self.name == 'string':
            raise ValueError('NAME IS REQUIRED')
        return self