from fastapi import APIRouter, HTTPException, Request

from src.utils.roles import roles_required
from db_config.enums import UserRole
from db_config.db_connection import session
from db_config.db_tables import CarouselImage
from src.components.carousel.schemas import CarouselImage, UpdateCarouselImage
from .repository import CarouselRepository

ADMIN = UserRole.admin

carousel_router = APIRouter(
    prefix="/carousel",
    tags=["Carousel"]
    )

carousel_repo = CarouselRepository(session)

@carousel_router.get("/")
def get_carousel():
    return carousel_repo.get_carousel()

@carousel_router.get("/{image_id}")
def get_image_by_id(request: Request, id):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    image = carousel_repo.get_carousel_image(id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@carousel_router.post("/")
def create_image(request: Request, data: CarouselImage):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    new = data.model_dump()
    return carousel_repo.create_carousel_image(new)

@carousel_router.put("/")
def update_carousel_iamge(request: Request, data: UpdateCarouselImage):
    token = request.cookies.get("access_token")
    roles_required([ADMIN], token)
    image_exst = carousel_repo.get_carousel_image(data.id)
    if not image_exst:
        raise HTTPException(status_code=404, detail="Image not found")
    return carousel_repo.update_carousel_image(data)

@carousel_router.delete("/{image_id}")
def delete_image(id):
    return carousel_repo.delete_carousel_image(id)