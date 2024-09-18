from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from uuid import uuid4

from src.utils.roles import roles_required
from src.components.auth.controller import oauth2_scheme
from db_config.enums import UserRole
from db_config.db_connection import session
from db_config.db_tables import CarouselImage
from src.components.carousel.schemas import CarouselReq, CarouselRes
from .repository import CarouselRepository

ADMIN = UserRole.admin

carousel_router = APIRouter(
    prefix="/carousel",
    tags=["Carousel"],
    )

carousel_repo = CarouselRepository(session)

@carousel_router.get("/")
def get_carousel_imges() -> list[CarouselRes]:
    return carousel_repo.get_carousel_imges()

@carousel_router.get("/{image_id}")
def get_image_by_id(id, token: Annotated[str, Depends(oauth2_scheme)]) -> CarouselRes:
    roles_required([ADMIN], token)
    image = carousel_repo.get_carousel_image(id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@carousel_router.post("/")
def create_image(data: CarouselReq, token: Annotated[str, Depends(oauth2_scheme)]):
    roles_required([ADMIN], token)
    new_image = CarouselImage(id=str(uuid4()), **data.model_dump())
    return carousel_repo.create_carousel_image(new_image)

@carousel_router.put("/")
def update_carousel_iamge(data: CarouselReq, token: Annotated[str, Depends(oauth2_scheme)]):
    roles_required([ADMIN], token)
    image_exst = carousel_repo.get_carousel_image(data.id)
    if not image_exst:
        raise HTTPException(status_code=404, detail="Image not found")
    return carousel_repo.update_carousel_image(data)

@carousel_router.delete("/{image_id}")
def delete_image(id, token: Annotated[str, Depends(oauth2_scheme)]):
    roles_required([ADMIN], token)
    return carousel_repo.delete_carousel_image(id)