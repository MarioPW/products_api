import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from main import app
from src.components.carousel.repository import CarouselRepository
from db_config.db_tables import CarouselImage

client = TestClient(app)

# Mocks
mock_session = MagicMock()
carousel_repo = CarouselRepository(mock_session)

# Patch the repository in the router with the mock
@pytest.fixture(autouse=True)
def patch_repo():
    with patch('src.components.carousel.repository', carousel_repo):
        yield

@pytest.fixture
def mock_carousel_repo(carousel_repo):
    mock_session = MagicMock()
    carousel_repo = CarouselRepository(mock_session)
    app.dependency_overrides[CarouselRepository] = lambda: carousel_repo
    return carousel_repo

# Test for getting the entire carousel
def test_get_carousel(mock_carousel_repo):
    mock_data = [CarouselImage(id="1", img_url="url1", slug="slug1")]
    mock_carousel_repo.return_value=mock_data

    response = client.get("/api/v1/carousel")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "img_url": "url1", "slug": "slug1"}]

# Test for getting an image by ID
def test_get_image_by_id():
    mock_data = CarouselImage(id="1", img_url="url1", slug="slug1")
    carousel_repo.get_carousel_image = MagicMock(return_value=mock_data)

    response = client.get("/api/v1/carousel/1")
    assert response.status_code == 200
    assert response.json() == {"id": "1", "img_url": "url1", "slug": "slug1"}

def test_get_image_by_id_not_found():
    carousel_repo.get_carousel_image = MagicMock(return_value=None)

    response = client.get("/carousel/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Image not found"}

# Test for creating an image
def test_create_image():
    mock_data = {"id": "1", "img_url": "url1", "slug": "slug1"}
    carousel_repo.create_carousel_image = MagicMock(return_value=mock_data)

    response = client.post("/carousel/", json=mock_data)
    assert response.status_code == 200
    assert response.json() == mock_data

# Test for updating an image
def test_update_carousel_image():
    mock_data = {"id": "1", "img_url": "url1", "slug": "slug1"}
    carousel_repo.get_carousel_image = MagicMock(return_value=mock_data)
    carousel_repo.update_carousel_image = MagicMock(return_value=mock_data)

    response = client.put("/carousel/", json=mock_data)
    assert response.status_code == 200
    assert response.json() == mock_data

def test_update_carousel_image_not_found():
    carousel_repo.get_carousel_image = MagicMock(return_value=None)

    response = client.put("/carousel/", json={"id": "1", "img_url": "url1", "slug": "slug1"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Image not found"}

# Test for deleting an image
def test_delete_image():
    carousel_repo.delete_carousel_image = MagicMock(return_value={"detail": "Image deleted"})

    response = client.delete("/carousel/1")
    assert response.status_code == 200
    assert response.json() == {"detail": "Image deleted"}
