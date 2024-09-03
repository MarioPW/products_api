import pytest
from fastapi.testclient import TestClient
from main import app
from src.components.users.service import UserService
from src.components.users.schemas import UserUpdateReq, ResetPasswordReq, UserRegister
from db_config.db_tables import User, ResetPasswordToken
from src.utils.roles import roles_required
from src.utils.email_handler import EmailHandler
from src.utils.jwt_handler import TokenHandler
from db_config.enums import UserRole
from src.components.users.repository import UserRepository
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import json
import uuid
import faker
from datetime import datetime, timedelta
from src.utils.password_hash import get_password_hash


fake = faker.Faker()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_service_mock(mocker):
    return mocker.patch("src.components.users.service.UserService")

@pytest.fixture
def roles_required_mock(mocker):
    return mocker.patch("src.utils.roles.roles_required")

@pytest.fixture
def valid_token():
    return "valid_token"

@pytest.fixture
def admin_token():
    return UserRole.admin

@pytest.fixture
def fake_user():
    return User(
    user_id= str(uuid.uuid4()),
    name= fake.name(),
    email= fake.unique.email(),
    password_hash= fake.sha256(),
    creation_date= datetime.now(),
    role= UserRole.user, 
    confirmation_code= fake.random_int(min=1000, max=9999),
    attempts_to_change_password= 0,
    active= False
    )

@pytest.fixture
def fake_register():
    return UserRegister(
        user_name= fake.name(),
        email= fake.email(),
        password= "secure_password",
        password_confirm= "secure_password"
    )

@pytest.fixture
def fake_reset_password_token():
    return ResetPasswordToken(
        id=fake.random_int(min=1, max=1000),
        user_id=str(fake.uuid4()),
        token=fake.sha256(),
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=10)
    )
@pytest.fixture
def fake_reset_password_req():
    return ResetPasswordReq(
        email=fake.email(),
        token=fake.uuid4(),
        password1="secure_password",
        password2="secure_password"
    )
@pytest.fixture
def fake_user_updates():
    return UserUpdateReq(
        name=fake.name(),
        email=fake.email(),
        current_password=fake.password(),
        new_password=fake.password()
    )
@pytest.fixture
def fake_hashed_password():
    return get_password_hash(fake.password())

#### TEST ####


def test_get_all_users(client, user_service_mock, roles_required_mock, admin_token):
    # Mock the get_all_users method
    user_service_mock.return_value.get_all_users.return_value = ["user1", "user2", "user3"]

    # Make the request to the endpoint
    response = client.get("/users")

    # Verify that roles_required was called once with the correct arguments
    roles_required_mock.assert_called_once_with([UserRole.admin], admin_token)

    # Assert the response
    assert response.status_code == 200
    assert response.json() == ["user1", "user2", "user3"]

# def test_get_user_by_id(client, user_service_mock, admin_token, fake_user):
#     user_service_mock.get_user_by_id.return_value = fake_user

#     response = client.get(f"/users/user_id/{fake_user.user_id}", headers={"Authorization": f"Bearer {admin_token}"})

#     assert response.status_code == 200
#     assert response.json() == fake_user.dict()

# def test_create_register_submition(client, user_service_mock, fake_register):
#     user_service_mock.get_user_by_email.return_value = None
#     user_service_mock.create_register_submition.return_value = {"message": "User created"}

#     response = client.post("/users/register", json=fake_register.dict())

#     assert response.status_code == 200
#     assert response.json() == {"message": "User created"}

# def test_create_register_submition_user_exists(client, user_service_mock, fake_register):
#     user_service_mock.get_user_by_email.return_value = True

#     response = client.post("/users/register", json=fake_register.dict())

#     assert response.status_code == 409
#     assert response.json() == {"detail": f"User with mail {fake_register.email} already exists."}

# def test_confirm_user(client, user_service_mock, fake_confirmation_code = 1234):
#     user_service_mock.get_user_by_confirmation_code.return_value = fake_user
#     user_service_mock.confirm_user.return_value = {"message": "User confirmed"}

#     response = client.post("/users/confirm_user", json=fake_confirmation_code.dict())

#     assert response.status_code == 200
#     assert response.json() == {"message": "User confirmed"}

# def test_login(client, user_service_mock, mocker):
#     fake_login_data = OAuth2PasswordRequestForm(username="test@example.com", password="password")
#     mocker.patch("fastapi.security.OAuth2PasswordRequestForm.__call__", return_value=fake_login_data)
#     user_service_mock.login.return_value = {"access_token": "fake_access_token", "token_type": "bearer"}

#     response = client.post("/users/login", data=fake_login_data.dict())

#     assert response.status_code == 200
#     assert response.json() == {"access_token": "fake_access_token", "token_type": "bearer"}

# def test_update_user(client, user_service_mock, valid_token, fake_user_updates):
#     user_service_mock.update_user.return_value = {"message": "User updated"}

#     response = client.put("/users/", headers={"Authorization": f"Bearer {valid_token}"}, json=fake_user_updates.dict())

#     assert response.status_code == 200
#     assert response.json() == {"message": "User updated"}

# def test_delete_user(client, user_service_mock, admin_token, fake_user):
#     user_service_mock.delete_user.return_value = {"message": "User deleted"}

#     response = client.delete(f"/users/{fake_user.user_id}", headers={"Authorization": f"Bearer {admin_token}"})

#     assert response.status_code == 200
#     assert response.json() == {"message": "User deleted"}

# def test_forgot_password(client, user_service_mock, fake_user):
#     user_service_mock.forgot_password.return_value = {"message": "Password reset link sent"}

#     response = client.post(f"/users/forgot_password/{fake_user.email}")

#     assert response.status_code == 200
#     assert response.json() == {"message": "Password reset link sent"}

# def test_reset_password(client, user_service_mock, fake_reset_password_req):
#     user_service_mock.reset_password.return_value = {"message": "Password reset successful"}

#     response = client.post("/users/reset_password/", json=fake_reset_password_req.dict())

#     assert response.status_code == 200
#     assert response.json() == {"message": "Password reset successful"}
