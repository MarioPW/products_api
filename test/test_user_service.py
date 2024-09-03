from fastapi import HTTPException
import pytest
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import json
import uuid
import faker
from src.components.users.schemas import UserUpdateReq, ResetPasswordReq, UserRegister
from db_config.db_tables import User, ResetPasswordToken
from db_config.enums import UserRole
from src.components.users.service import UserService
from src.components.users.repository import UserRepository
from src.utils.email_handler import EmailHandler
from src.utils.jwt_handler import TokenHandler
from src.utils.password_hash import get_password_hash

#### FIXTURES ####

fake = faker.Faker() 
@pytest.fixture
def user_service_instance():
    return UserService(UserRepository, EmailHandler, TokenHandler, UserRole)
@pytest.fixture
def mock_OAuth2PasswordRequestForm():
    return OAuth2PasswordRequestForm(username="test@example.com",
            password="password123")
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

class TestUserService:

    def test_get_all_users(self, user_service_instance, mocker):
        # Mocks
        mock_get_all_users = mocker.patch.object(user_service_instance.user_repository, 'get_all_users', return_value=["user1", "user2", "user3"])
        result = user_service_instance.get_all_users()
        mock_get_all_users.assert_called_once()
        assert result == ["user1", "user2", "user3"]
    
    def test_get_user_by_email(self, user_service_instance, mocker):
        # Mocks
        mock_get_user_by_email = mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value={"user_id": 1, "name": "test_user"})
        # Act & asserts
        result = user_service_instance.get_user_by_email("test@example.com")
        mock_get_user_by_email.assert_called_once_with("test@example.com")
        assert result == {"user_id": 1, "name": "test_user"}

    def test_get_user_by_id(self, user_service_instance, fake_user, mocker):
        # Mocks
        mock_get_user_by_id = mocker.patch.object(user_service_instance.user_repository, 'get_user_by_id', return_value=fake_user)
        # Act & asserts
        result = user_service_instance.get_user_by_id(fake_user.user_id)
        mock_get_user_by_id.assert_called_once_with(fake_user.user_id)
        assert result == fake_user

    def test_get_user_by_confirmation_code(self, user_service_instance, mocker):
        # Mocks
        confirmation_code = 1234
        mock_get_user_by_confirmation_code = mocker.patch.object(
            user_service_instance.user_repository,
            'get_user_by_confirmation_code',
            return_value={"user_id": 1, "name": "test_user", "confirmation_code": confirmation_code}
        )
        # Act & Assertions
        result = user_service_instance.get_user_by_confirmation_code(confirmation_code)
        mock_get_user_by_confirmation_code.assert_called_once_with(confirmation_code)
        assert result == {"user_id": 1, "name": "test_user", "confirmation_code": confirmation_code}

    def test_create_register_submition(self, user_service_instance, fake_register, fake_user, mocker):
        # Mocks
        mock_email_handler_class = mocker.patch.object(user_service_instance, 'email_handler')
        mock_email_handler_instance = mock_email_handler_class.return_value
        mock_email_handler_instance.send_verification_email.return_value = None
        mock_email_handler_instance.get_verification_code.return_value = 'fake_verification_code'
        mock_create_user = mocker.patch.object(user_service_instance.user_repository, 'create_user')
        
        # Action
        user_service_instance.create_register_submition(fake_register)

        # Assertions
        mock_email_handler_instance.send_verification_email.assert_called_once()
        mock_create_user.assert_called_once()
       
    def test_create_register_submition_failure(self, user_service_instance, fake_register, mocker):
        # Mocks
        mock_email_handler_class = mocker.patch.object(user_service_instance, 'email_handler')
        mock_email_handler_instance = mock_email_handler_class.return_value
        mock_email_handler_instance.send_verification_email.return_value = None
        mock_email_handler_instance.get_verification_code.return_value = 'fake_verification_code'
        # Simulate exception
        mocker.patch('src.components.users.service.get_password_hash', side_effect=Exception("Simulated creation failure"))
        
        with pytest.raises(HTTPException) as excinfo:
            user_service_instance.create_register_submition(fake_register)
        # Assertions
        assert excinfo.value.status_code == 400
        assert "Something went wrong creating register model in service" in excinfo.value.detail
        mock_email_handler_instance.send_verification_email.assert_called_once()

    def test_confirm_user(self, user_service_instance, mocker):
        # Mocks
        unconfirmed_user = User(user_id='abcd', name="test_user", role=UserRole.unconfirmed, confirmation_code=1234)
        confirmed_user = {
            "role": UserRole.user,
            "confirmation_code": 1
        }
        mock_update_user = mocker.patch.object(
            user_service_instance.user_repository,
            'update_user',
            return_value=confirmed_user
        )
        # Act & asserttions
        result = user_service_instance.confirm_user(unconfirmed_user)
        mock_update_user.assert_called_once_with(unconfirmed_user.user_id, confirmed_user)
        assert result == confirmed_user

    def test_confirm_user_with_invalid_role(self, user_service_instance):
        # Mocks
        unconfirmed_user = User(user_id=1)
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.confirm_user(unconfirmed_user)
        # Assertions
        assert exc_info.value.status_code == 500
        assert "Error updating user in repository" in exc_info.value.detail

    def test_login(self, user_service_instance, mocker, fake_user, mock_OAuth2PasswordRequestForm):
        # Mocks
        user_data = mock_OAuth2PasswordRequestForm
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=fake_user)
        mock_verify_password = mocker.patch("src.components.users.service.verify_password")
        mock_create_access_token = mocker.patch("src.components.users.service.TokenHandler.create_access_token")
        mock_verify_password.return_value = True
        mock_create_access_token.return_value="fake_access_token"
        # Act
        result = user_service_instance.login(user_data)
        # Assertions
        user_service_instance.user_repository.get_user_by_email.assert_called_once_with(user_data.username)
        mock_verify_password.assert_called_once_with(user_data.password, fake_user.password_hash)
        mock_create_access_token.assert_called_once_with({
            "user_id": fake_user.user_id,
            "name": fake_user.name,
            "role": fake_user.role
        })
        expected_result = {
            "access_token": "fake_access_token",
            "token_type": "bearer",
        }
        assert result == expected_result
    
    def test_login_with_invalid_password(self, user_service_instance, mocker, fake_user, mock_OAuth2PasswordRequestForm):
        # Mocks
        user_data = mock_OAuth2PasswordRequestForm
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=fake_user)
        mock_verify_password = mocker.patch("src.components.users.service.verify_password")
        mock_verify_password.return_value = False
        mock_create_access_token = mocker.patch("src.components.users.service.TokenHandler.create_access_token")
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.login(user_data)
        # Assertions
        assert exc_info.value.status_code == 400
        assert "Incorrect User or Password" in exc_info.value.detail
        assert mock_create_access_token.call_count == 0

    def test_login_with_invalid_user(self, user_service_instance, mocker, mock_OAuth2PasswordRequestForm):
        # Mocks
        user_data = mock_OAuth2PasswordRequestForm
        mock_verify_password = mocker.patch("src.components.users.service.verify_password")
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=None)
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.login(user_data)
        # Assertions
        assert exc_info.value.status_code == 404
        assert f'User {user_data.username} not found' in exc_info.value.detail
        assert mock_verify_password.call_count == 0

    def test_login_with_exception_role(self, user_service_instance, mocker, mock_OAuth2PasswordRequestForm):
        # Mocks
        user_data = mock_OAuth2PasswordRequestForm

        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=User(user_id=1, name="test_user", role=UserRole.unconfirmed))
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.login(user_data)
        # Assertions
        assert exc_info.value.status_code == 400
        assert f"User {user_data.username} not authorized in UserService.login()" in exc_info.value.detail

    def test_login_with_token_creation_failure(self, user_service_instance, mocker, fake_user, mock_OAuth2PasswordRequestForm):
        # Mocks
        user_data = mock_OAuth2PasswordRequestForm
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=fake_user)
        mock_verify_password = mocker.patch("src.components.users.service.verify_password")
        mock_create_access_token = mocker.patch("src.components.users.service.TokenHandler.create_access_token")
        
        # Exception
        mock_verify_password.return_value = True
        mock_create_access_token.side_effect = Exception("Token creation failed")
        
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.login(user_data)
        
        # Assertions
        assert exc_info.value.status_code == 400
        assert "Error creating user token: Token creation failed" in exc_info.value.detail
        user_service_instance.user_repository.get_user_by_email.assert_called_once_with(user_data.username)
        mock_verify_password.assert_called_once_with(user_data.password, fake_user.password_hash)
        mock_create_access_token.assert_called_once_with({
            "user_id": fake_user.user_id,
            "name": fake_user.name,
            "role": fake_user.role
        })

    def test_forgot_password(self, user_service_instance, fake_user, mocker):
        # Mocks
        email = "test@example.com"
        attempts_update = {"attempts_to_change_password": fake_user.attempts_to_change_password + 1}
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=fake_user)
        mock_update_user = mocker.patch.object(user_service_instance.user_repository, 'update_user')
        mock_email_handler = mocker.patch.object(user_service_instance, 'email_handler', return_value=mocker.MagicMock(
            send_change_password_email=mocker.MagicMock(),
            get_reset_password_code=mocker.MagicMock(return_value="reset_code")
        ))
        mock_save_reset_password = mocker.patch.object(user_service_instance.user_repository, 'save_reset_password_token')
        # Act
        response = user_service_instance.forgot_password(email)
        # Assertions
        mock_update_user.assert_called_once_with(fake_user.user_id, attempts_update)
        mock_save_reset_password.assert_called_once()
        mock_email_handler.return_value.send_change_password_email.assert_called_once()
        mock_email_handler.return_value.get_reset_password_code.assert_called_once()
        
        assert response.status_code == 200
        assert json.loads(response.body.decode('utf-8')) == {"message": f'Email to "{email}" sent successfully.'}

    def test_forgot_password_user_exist_Exception(self, user_service_instance, mocker):
        # Mocks
        email = "test@example.com"
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=None)
        mocker.patch.object(EmailHandler, 'send_change_password_email')
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.forgot_password(email)
        # Assertions
        assert exc_info.value.detail == f'User "{email}" not found'
        assert exc_info.value.status_code == 404
        EmailHandler.send_change_password_email.assert_not_called()

    def test_forgot_password_exception_EmailHandler(self, user_service_instance, fake_user, mocker):
        # Mocks
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_email', return_value=fake_user)
        email_handler = mocker.patch.object(EmailHandler, 'send_change_password_email')
        email_handler.side_effect = HTTPException(status_code=400, detail=f"Error sending change password email:")
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.forgot_password(fake_user.email)
        # Acts & Assertions
        user_repository_save_reset_password_token = mocker.patch.object(user_service_instance.user_repository, 'save_reset_password_token')

        user_repository_save_reset_password_token.assert_not_called()
        assert "Error updating user in repository" in exc_info.value.detail
    
    def test_reset_password(sef, user_service_instance, fake_reset_password_token, fake_reset_password_req, mocker):
        # Mocks
        mocker.patch.object(user_service_instance.user_repository, 'get_reset_password_token', return_value=fake_reset_password_token)

        hashed_password = "$2b$12$fixedhashvaluefixedhashvaluefixedhashvaluefixedhashvalue"
        mock_update_user = mocker.patch.object(user_service_instance.user_repository, 'update_user')
        mocker.patch('src.components.users.service.get_password_hash', return_value=hashed_password)
        # Acts & Assertions
        result = user_service_instance.reset_password(fake_reset_password_req) 
        fake_password_update = {
            "password_hash": hashed_password
        }
        mock_update_user.assert_called_once_with(fake_reset_password_token.user_id, fake_password_update)
        
    def test_update_user(self, user_service_instance, fake_user, fake_user_updates, mocker):
        # Mocks
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_id', return_value=fake_user)
        mocker.patch('src.components.users.service.verify_password', return_value=True)
        mocker.patch('src.components.users.service.get_password_hash', return_value="fake_hashed_password")
        mock_update_user = mocker.patch.object(user_service_instance.user_repository, 'update_user', return_value=fake_user)
        # Acts & Assertions
        result = user_service_instance.update_user(fake_user.user_id, fake_user_updates)
        
        updated_user_data = {
            "name": fake_user_updates.name,
            "email": fake_user_updates.email,
            "password_hash": "fake_hashed_password"
        }
        mock_update_user.assert_called_once_with(fake_user.user_id, updated_user_data)
        assert result == fake_user
    
    def test_update_user_user_not_found(self, user_service_instance, fake_user_updates, mocker):
        # Mocks
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_id', return_value=None)

        mock_verify_apssword = mocker.patch('src.components.users.service.verify_password')
        # Failure
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.update_user("non_existing_user_id", fake_user_updates)
        # Assertions
        assert mock_verify_apssword.call_count == 0
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == f"User 'non_existing_user_id' not found"
    
    def test_update_user_verify_password_exception(self, user_service_instance, fake_user, fake_user_updates, mocker):
        # Mocks
        mocker.patch.object(user_service_instance.user_repository, 'get_user_by_id', return_value=fake_user)
        mocker.patch('src.components.users.service.verify_password', return_value=False)
        mock_update_user = mocker.patch.object(user_service_instance.user_repository, 'update_user', return_value=fake_user)
        # Failure 
        with pytest.raises(HTTPException) as exc_info:
            user_service_instance.update_user(fake_user.user_id, fake_user_updates)
        # Assertions
        assert mock_update_user.call_count == 0
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid password"
    
