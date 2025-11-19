import pytest
from types import SimpleNamespace
from unittest.mock import patch, Mock
from pyotp import TOTP, random_base32
from sqlalchemy.exc import IntegrityError
from app import db
from flask import url_for
from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


@pytest.fixture
def sample_user():
    """Reusable simple user-like object for unit tests."""
    return SimpleNamespace(
        email="test@example.com",
        password="test1234",
        two_factor_enabled=False,
        two_factor_secret=None,
    )


@pytest.fixture
def random_secret():
    """Return a fresh pyotp secret for tests that need one."""
    return random_base32()


def test_repoitory_create_no_commit(test_client, clean_database):
    with test_client.application.app_context():
        data = {"email": "no_commit@example.com", "password": "1234"}
        user = UserRepository().create(commit=False, **data)

        assert user.email == "no_commit@example.com"
        assert user is not None


def test_repository_save_changes_fail_rollback(test_client, clean_database):
    with test_client.application.app_context():
        real_user = UserRepository().create(email="error@example.com", password="1234")
    with patch.object(db.session, 'commit', side_effect=IntegrityError("msg", "params", "orig")), \
        patch.object(db.session, 'rollback') as mock_rollback:

        repo_fail = UserRepository()

        with test_client.application.app_context():
            with pytest.raises(IntegrityError):
                repo_fail.save_changes(real_user)
        mock_rollback.assert_called_once()


def test_repoitory_create(test_client, clean_database):
    data = {"email": "test@example.com", "password": "1234"}
    email = UserRepository().create(**data).email
    assert email == "test@example.com"


def test_repository_create_fail(test_client, clean_database):
    data = {"email": "", "password": "1234"}
    user = UserRepository().create(**data)
    assert user.email == ""


def test_repository_save_changes(test_client, clean_database):
    user = UserRepository().create(email="toreplace@example.com", password="1234")
    user.email = "test_updated@example.com"
    updated_user = UserRepository().save_changes(user)
    assert updated_user.email == "test_updated@example.com"


def test_repository_save_changes_fail(test_client, clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "",
        "password": "1234",
    }

    with patch("app.modules.auth.services.UserRepository"), patch(
        "app.modules.auth.services.UserProfileRepository"
    ):
        service = AuthenticationService()
        with pytest.raises(ValueError, match="Email is required."):
            service.create_with_profile(**data)


def test_service_login_success(test_client, clean_database):
    with test_client.application.app_context():
        UserRepository().create(email="test@example.com", password="test1234")

    with test_client.application.test_request_context():
        login_url = url_for("auth.login")
        logout_url = url_for("auth.logout")

    response = test_client.post(
        login_url,
        data=dict(email="test@example.com", password="test1234"),
        follow_redirects=True
    )

    assert response.request.path != login_url, "Login was unsuccessful, still on login page."

    test_client.get(logout_url, follow_redirects=True)


def test_service_login_fail_bad_password(test_client, clean_database):
    with test_client.application.app_context():
        UserRepository().create(email="test@example.com", password="test1234")

    with test_client.application.test_request_context():
        login_url = url_for("auth.login")

    response = test_client.post(
        login_url,
        data=dict(email="test@example.com", password="basspassword"),
        follow_redirects=True
    )

    assert response.request.path == login_url, "Login was successful when it should have failed."


@patch("app.modules.auth.services.login_user")
def test_service_login_fail_no_user(mock_login_user):
    service = AuthenticationService()
    result = service.login(user=None, remember=True)

    assert result is False
    mock_login_user.assert_not_called()


@patch('app.modules.auth.services.login_user')
@patch('app.modules.auth.services.UserRepository')
def test_service_login_initial_success(MockUserRepo, mock_login_user):
    mock_user = Mock(check_password=lambda p: p == 'correct_password')
    MockUserRepo.return_value.get_by_email.return_value = mock_user

    service = AuthenticationService()
    result = service.login_initial('test@example.com', 'correct_password')

    assert result is True
    mock_login_user.assert_called_once_with(mock_user, remember=True)
    MockUserRepo.return_value.get_by_email.assert_called_once_with('test@example.com')


@patch('app.modules.auth.services.login_user')
@patch('app.modules.auth.services.UserRepository')
def test_service_login_initial_fail_bad_password(MockUserRepo, mock_login_user):
    mock_user = Mock(check_password=lambda p: p == 'correct_password')
    MockUserRepo.return_value.get_by_email.return_value = mock_user

    service = AuthenticationService()
    result = service.login_initial('test@example.com', 'wrong_password')

    assert result is False
    mock_login_user.assert_not_called()
    MockUserRepo.return_value.get_by_email.assert_called_once_with('test@example.com')


@patch('app.modules.auth.services.login_user')
@patch('app.modules.auth.services.UserRepository')
def test_service_login_initial_fail_no_user(MockUserRepo, mock_login_user):
    MockUserRepo.return_value.get_by_email.return_value = None

    service = AuthenticationService()
    result = service.login_initial('nonexistent@example.com', 'any_password')

    assert result is False
    mock_login_user.assert_not_called()
    MockUserRepo.return_value.get_by_email.assert_called_once_with('nonexistent@example.com')


@patch('app.modules.auth.services.UserProfileRepository')
@patch('app.modules.auth.services.AuthenticationService.create')
@patch('app.modules.auth.services.UserRepository')
def test_service_create_with_profile_success(MockUserRepo, mock_auth_service_create, MockProfileRepo):
    mock_user = Mock(id=100, email="test@example.com", check_password=Mock(), password="hashed")
    mock_auth_service_create.return_value = mock_user
    mock_session = Mock()
    MockUserRepo.return_value.session = mock_session

    data = {
        "email": "test@example.com",
        "password": "1234password",
        "name": "John",
        "surname": "Doe",
    }
    service = AuthenticationService()

    returned_user = service.create_with_profile(**data)

    mock_auth_service_create.assert_called_once_with(
        commit=False,
        email="test@example.com",
        password="1234password"
    )

    expected_profile_data = {
        "name": "John",
        "surname": "Doe",
        "user_id": 100
    }
    MockProfileRepo.return_value.create.assert_called_once_with(**expected_profile_data)

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()

    assert returned_user == mock_user
    assert returned_user.email == "test@example.com"


def test_service_create_with_profile_fail_no_password(test_client):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "test@example.com",
        "password": "",
    }
    with patch("app.modules.auth.services.UserRepository"), patch(
        "app.modules.auth.services.UserProfileRepository"
    ):
        service = AuthenticationService()
        with pytest.raises(ValueError, match="Password is required."):
            service.create_with_profile(**data)


def test_service_create_with_profile_fail_no_name(test_client):
    data = {
        "name": "",
        "surname": "Foo",
        "email": "test@example.com",
        "password": "1234",
    }
    with patch("app.modules.auth.services.UserRepository"), patch(
        "app.modules.auth.services.UserProfileRepository"
    ):
        service = AuthenticationService()
        with pytest.raises(ValueError, match="Name is required."):
            service.create_with_profile(**data)


def test_service_create_with_profile_fail_no_surname(test_client):
    data = {
        "name": "Test",
        "surname": "",
        "email": "test@example.com",
        "password": "1234",
    }
    with patch("app.modules.auth.services.UserRepository"), patch(
        "app.modules.auth.services.UserProfileRepository"
    ):
        service = AuthenticationService()
        with pytest.raises(ValueError, match="Surname is required."):
            service.create_with_profile(**data)


@patch('app.modules.auth.services.AuthenticationService.update')
def test_service_update_profile_success(mock_update):
    profile_id = 55
    mock_form = Mock()
    mock_form.validate.return_value = True
    mock_form.data = {'name': 'Pedro', 'surname': 'Gomez'}
    mock_updated_profile = Mock(id=profile_id, name='Pedro', surname='Gomez')
    mock_update.return_value = mock_updated_profile

    service = AuthenticationService()

    updated_instance, errors = service.update_profile(profile_id, mock_form)
    assert errors is None
    assert updated_instance == mock_updated_profile

    mock_update.assert_called_once_with(
        profile_id,
        name='Pedro',
        surname='Gomez'
    )


@patch('app.modules.auth.services.AuthenticationService.update')
def test_service_update_profile_validation_fail(mock_update):
    profile_id = 55
    mock_form = Mock()
    mock_form.validate.return_value = False
    mock_form.errors = {'name': ['El nombre es obligatorio.']}

    service = AuthenticationService()

    updated_instance, errors = service.update_profile(profile_id, mock_form)
    assert updated_instance is None
    assert errors == {'name': ['El nombre es obligatorio.']}
    mock_update.assert_not_called()


def test_is_email_available(test_client, clean_database):
    email = "test@example.com"
    service = AuthenticationService()
    assert service.is_email_available(email) is True


def test_is_email_not_available(test_client, clean_database):
    email = "user1@example.com"
    UserRepository().create(email=email, password="1234")
    service = AuthenticationService()
    assert service.is_email_available(email) is False


@patch('app.modules.auth.services.current_user')
def test_service_get_authenticated_user_success(mock_current_user):
    mock_current_user.is_authenticated = True
    mock_current_user.email = "test@auth.com"

    service = AuthenticationService()
    user = service.get_authenticated_user()

    assert user == mock_current_user
    assert user.email == "test@auth.com"


@patch('app.modules.auth.services.current_user')
def test_service_get_authenticated_user_fail(mock_current_user):
    mock_current_user.is_authenticated = False

    service = AuthenticationService()
    user = service.get_authenticated_user()

    assert user is None


@patch('app.modules.auth.services.current_user')
def test_service_get_authenticated_user_profile_success(mock_current_user):
    mock_profile = Mock()
    mock_profile.name = "Auth Profile"
    mock_current_user.is_authenticated = True
    mock_current_user.profile = mock_profile

    service = AuthenticationService()
    profile = service.get_authenticated_user_profile()

    assert profile == mock_profile
    assert profile.name == "Auth Profile"


@patch('app.modules.auth.services.current_user')
def test_service_get_authenticated_user_profile_fail(mock_current_user):
    mock_current_user.is_authenticated = False

    service = AuthenticationService()
    profile = service.get_authenticated_user_profile()

    assert profile is None


@patch('app.modules.auth.services.os.path.join', side_effect=lambda *args: '/'.join(args))
@patch('app.modules.auth.services.uploads_folder_name')
def test_service_temp_folder_by_user(mock_uploads_folder_name, mock_os_path_join):
    mock_uploads_folder_name.return_value = '/var/www/uploads'

    mock_user_int = Mock(id=42)

    service = AuthenticationService()

    expected_path_int = '/var/www/uploads/temp/42'
    result_int = service.temp_folder_by_user(mock_user_int)
    assert result_int == expected_path_int

    mock_os_path_join.assert_called_with('/var/www/uploads', 'temp', '42')
    mock_user_str = Mock(id='uuid-123')

    expected_path_str = '/var/www/uploads/temp/uuid-123'
    result_str = service.temp_folder_by_user(mock_user_str)

    assert result_str == expected_path_str
    mock_os_path_join.assert_any_call('/var/www/uploads', 'temp', 'uuid-123')


def test_service_save_user_changes(test_client, clean_database):
    user = UserRepository().create(email="test@example.com", password="1234")
    user.password = "newpassword"
    result = AuthenticationService().save_user_changes(user)
    assert result.password != "1234"
    assert result.password == "newpassword"


def test_service_save_user_changes_fail(test_client):
    user = SimpleNamespace(**vars(test_client))
    user.email = None

    with patch("app.modules.auth.services.UserRepository") as UserRepoMock:
        repo_inst = UserRepoMock.return_value
        repo_inst.save_changes.side_effect = Exception("save failed")
        service = AuthenticationService()
        with pytest.raises(Exception):
            service.save_user_changes(user)


def test_service_check_credentials_success(test_client):
    email = "test@example.com"
    password = "1234"

    dummy_user = SimpleNamespace()
    dummy_user.check_password = lambda p: p == password

    with patch("app.modules.auth.services.UserRepository") as UserRepoMock:
        repo_inst = UserRepoMock.return_value
        repo_inst.get_by_email.return_value = dummy_user
        service = AuthenticationService()
        user = service.check_credentials(email, password)
        assert user is not None


def test_service_check_credentials_fail(test_client):
    email = "test@example.com"
    password = "wrongpassword"

    dummy_user = SimpleNamespace()
    dummy_user.check_password = lambda p: False

    with patch("app.modules.auth.services.UserRepository") as UserRepoMock:
        repo_inst = UserRepoMock.return_value
        repo_inst.get_by_email.return_value = dummy_user
        service = AuthenticationService()
        user = service.check_credentials(email, password)
        assert user is None


def test_service_check_credentials_no_user(test_client):
    email = "nonexistent@example.com"
    password = "1234"

    with patch("app.modules.auth.services.UserRepository") as UserRepoMock:
        repo_inst = UserRepoMock.return_value
        repo_inst.get_by_email.return_value = None
        service = AuthenticationService()
        user = service.check_credentials(email, password)
        assert user is None


def test_service_encode_qr_code_data(test_client):
    data = (
        "otpauth://totp/TestApp:nonexistent@example.com?"
        "secret=MYSECRET&issuer=TestApp"
    )
    encoded_data = AuthenticationService().encode_qr_code(data)
    assert isinstance(encoded_data, str)
    assert len(encoded_data) > 0


@patch('app.modules.auth.services.pyotp.TOTP')
@patch.object(AuthenticationService, 'save_user_changes')
def test_service_verify_2fa_success_and_enables(mock_save_user_changes, MockTOTP, random_secret):
    secret = random_secret
    mock_user = Mock(two_factor_secret=secret.encode('utf-8'), two_factor_enabled=False)
    mock_totp_instance = Mock()
    mock_totp_instance.verify.return_value = True
    MockTOTP.return_value = mock_totp_instance

    service = AuthenticationService()
    test_code = '123456'
    result = service.verify_and_enable_2fa(mock_user, test_code)

    assert result is True
    assert mock_user.two_factor_enabled is True
    MockTOTP.assert_called_once_with(secret)
    mock_totp_instance.verify.assert_called_once_with(test_code)
    mock_save_user_changes.assert_called_once_with(mock_user)


@patch('app.modules.auth.services.pyotp.TOTP')
@patch.object(AuthenticationService, 'save_user_changes')
def test_service_verify_2fa_fail_incorrect_code(mock_save_user_changes, MockTOTP, random_secret):
    secret = random_secret
    mock_user = Mock(two_factor_secret=secret.encode('utf-8'), two_factor_enabled=False)
    mock_totp_instance = Mock()
    mock_totp_instance.verify.return_value = False
    MockTOTP.return_value = mock_totp_instance

    service = AuthenticationService()
    test_code = '000000'

    result = service.verify_and_enable_2fa(mock_user, test_code)

    assert result is False
    assert mock_user.two_factor_enabled is False
    mock_save_user_changes.assert_not_called()
    mock_totp_instance.verify.assert_called_once_with(test_code)


@patch('app.modules.auth.services.pyotp.TOTP')
@patch.object(AuthenticationService, 'save_user_changes')
def test_service_verify_2fa_fail_no_secret(mock_save_user_changes, MockTOTP):
    mock_user = Mock(two_factor_secret=None, two_factor_enabled=False)
    service = AuthenticationService()
    test_code = '123456'

    result = service.verify_and_enable_2fa(mock_user, test_code)
    assert result is False
    MockTOTP.assert_not_called()
    mock_save_user_changes.assert_not_called()


def test_service_verify_2fa_code_success(random_secret, sample_user):
    secret = random_secret
    secret_enc = secret.encode("utf-8")
    user = SimpleNamespace(**vars(sample_user))
    user.two_factor_enabled = True
    user.two_factor_secret = secret_enc
    result = AuthenticationService().verify_2fa_code(user, TOTP(secret).now())
    assert result is True


def test_service_verify_2fa_code_fail(random_secret, sample_user):
    secret = random_secret
    secret_enc = secret.encode("utf-8")
    user = SimpleNamespace(**vars(sample_user))
    user.two_factor_enabled = True
    user.two_factor_secret = secret_enc
    invalid_code = "000000"
    result = AuthenticationService().verify_2fa_code(user, invalid_code)
    assert result is False


def test_service_verify_2fa_code_not_enabled(test_client):
    user = SimpleNamespace(two_factor_enabled=False, two_factor_secret=None)
    result = AuthenticationService().verify_2fa_code(user, "123456")
    assert result is False


def test_service_verify_2fa_code_not_secret(test_client):
    user = SimpleNamespace(two_factor_enabled=True, two_factor_secret=None)
    result = AuthenticationService().verify_2fa_code(user, "123456")
    assert result is False


def test_service_generate_2fa_setup(sample_user):
    user = SimpleNamespace(**vars(sample_user))
    user.two_factor_enabled = False
    user.two_factor_secret = None

    with patch.object(AuthenticationService, "save_user_changes") as save_mock:
        with patch.object(AuthenticationService, "encode_qr_code") as encode_mock:
            save_mock.return_value = user
            encode_mock.return_value = "fake_qr"
            service = AuthenticationService()
            secret, uri, qr_base64 = service.generate_2fa_setup(user)
            assert isinstance(secret, str)
            assert isinstance(uri, str)
            assert isinstance(qr_base64, str)
            assert len(secret) > 0
            assert len(uri) > 0
            assert len(qr_base64) > 0
