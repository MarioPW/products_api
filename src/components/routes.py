from fastapi import APIRouter
from src.components.products.controller import  products_router
from src.components.users.controller import  users_router
from src.components.categories.controller import  categories_router
from src.components.carousel.controller import  carousel_router
from src.components.auth.controller import  auth_router

router = APIRouter()

router.include_router(products_router)
router.include_router(users_router)
router.include_router(carousel_router)
router.include_router(categories_router)
router.include_router(auth_router)