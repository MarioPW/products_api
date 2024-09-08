from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db_config.db_tables import Category

class CategotyRepository:
    def __init__(self, sess):
        self.sess: Session = sess

    def get_all_categories(self):
        try:
            return self.sess.query(Category).all()
        except Exception as e:
            print(e) # TODO: Implement a logger to register this errors
            raise HTTPException(status_code=500, detail=f"Error getting categories")

    def get_category_by_id(self, id):
        try:
            return self.sess.query(Category).filter(Category.id == id).first()
        except Exception as e:
            print(e) # TODO: Implement a logger to register this errors
            raise HTTPException(status_code=500, detail=f"Error getting category by id")

    def get_category_by_name(self, name):
        try:
            return self.sess.query(Category).filter(Category.name == name).first()
        except Exception as e:
            print(e) # TODO: Implement a logger to register this errors
            raise HTTPException(status_code=500, detail=f"Error getting category by name")

    def create_category(self, new_category):
        try:
            self.sess.add(new_category)
            self.sess.commit()
            return {"message": f"Category '{new_category.name}' created successfully"}
        except Exception as e:
            print(e) # TODO: Implement a logger to register this errors
            raise HTTPException(status_code=500, detail=f"Couldn't create category")

    def update_category(self, updates):
        try:
            self.sess.query(Category).filter(Category.id == updates['id']).update(updates)
            self.sess.commit()
            return JSONResponse(status_code=200, content=f"Category {updates['name']} updated successfully.")
        except Exception as e:
            print(e) # TODO: Implement a logger to register this errors
            raise HTTPException(status_code=500, detail=f"Couldn't update category")

    def delete_category(self, id):
        to_delete = self.sess.query(Category).filter(Category.id == id).first()
        if not to_delete:
            raise HTTPException(status_code=404, detail="Category not found")
        try:
            self.sess.delete(to_delete)
            self.sess.commit()
            return JSONResponse(status_code=200, content=f"Category {to_delete.name} deleted successfully.")
        except Exception as e:
            print(e) # TODO: Implement a logger to register this errors
            raise HTTPException(status_code=500, detail=f"Couldn't delete category")