from app.modules.conftest import login, logout
from app import db
from app.modules.auth.repositories import UserRepository
import pytest

from app.modules.auth.models import User
import pyotp


@pytest.fixture
def create_and_login_user(test_client, clean_database):
    def _create_and_login(email="user@example.com", password="test1234"):

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        login(test_client, email, password)
        return user

    return _create_and_login


def test_show_signup_form_get(test_client):
    logout(test_client)

    response = test_client.get('/signup/')

    assert response.status_code == 200
    assert b"Sign" in response.data
    assert b'name="name"' in response.data
    assert b'name="surname"' in response.data
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data


def test_signup_post_success_and_duplicate(test_client, clean_database):
    db.session.remove()
    db.drop_all()
    db.create_all()

    logout(test_client)
    signup_data = dict(
        name="Integration",
        surname="Tester",
        email="integration_new@example.com",
        password="testpass123",
    )
    response = test_client.post('/signup/', data=signup_data, follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/'

    user = UserRepository().get_by_email('integration_new@example.com')
    assert user is not None

    logout(test_client)
    response_dup = test_client.post('/signup/', data=dict(
        name="Integration",
        surname="Tester",
        email="integration_new@example.com",
        password="anotherpass",
    ), follow_redirects=True)

    assert response_dup.status_code == 200
    assert b"Email integration_new@example.com in use" in response_dup.data


def test_show_signup_form_user_authenticated(test_client, create_and_login_user):
    create_and_login_user(email="testuser@example.com")
    response = test_client.get('/signup/', follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/'


def test_signup_exception_handling(test_client, monkeypatch, clean_database):
    logout(test_client)

    def raise_exception(**kwargs):
        raise Exception("Simulated database error")

    monkeypatch.setattr(
        "app.modules.auth.routes.authentication_service.create_with_profile",
        raise_exception,
        raising=True,
    )

    signup_data = dict(
        name="Error",
        surname="Tester",
        email="error_tester@example.com",
        password="testpass123",
    )
    response = test_client.post('/signup/', data=signup_data)
    assert response.status_code == 200
    assert b"Error creating user: Simulated database error" in response.data
    assert b"Sign" in response.data
    assert b'name="name"' in response.data
    assert b'name="surname"' in response.data
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data


def test_login_redirects_authenticated_user(test_client, create_and_login_user):
    create_and_login_user(email="testuser@example.com")
    response = test_client.get('/login', follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/'


def test_login_user_two_factor_enabled(test_client, clean_database):
    logout(test_client)

    user = User(email="email@example.com", password="testpass123", two_factor_enabled=True)
    db.session.add(user)
    db.session.commit()
    login_data = dict(
        email="email@example.com",
        password="testpass123",
    )
    response = test_client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Introduce tu c\xc3\xb3digo de autenticaci\xc3\xb3n de dos factores." in response.data


def test_login_user_two_factor_disabled(test_client, clean_database):
    logout(test_client)

    user = User(email="email@example.com", password="testpass123", two_factor_enabled=False)
    db.session.add(user)
    db.session.commit()
    login_data = dict(
        email="email@example.com",
        password="testpass123",
    )
    response = test_client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/'


def test_login_invalid_credentials(test_client, clean_database):
    logout(test_client)

    login_data = dict(
        email="invalid@example.com",
        password="wrongpassword",
    )
    response = test_client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data


def test_login_get_renders_form(test_client):
    logout(test_client)

    response = test_client.get('/login')
    assert response.status_code == 200
    assert b"Log" in response.data
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data


def test_enable_two_factor_user_already_enabled(test_client, clean_database):
    logout(test_client)
    user = User(email="email@example.com", password="testpass123", two_factor_enabled=False)
    db.session.add(user)
    db.session.commit()

    login(test_client, "email@example.com", "testpass123")

    user.two_factor_enabled = True
    db.session.commit()

    response = test_client.get('/settings/2fa/enable', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/'


def test_enable_two_factor_new_user(test_client, clean_database):
    logout(test_client)
    user = User(email="email@example.com", password="testpass123", two_factor_enabled=False)
    db.session.add(user)
    db.session.commit()

    login(test_client, "email@example.com", "testpass123")
    response = test_client.get('/settings/2fa/enable', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/settings/2fa/enable'

    codeqr = pyotp.TOTP(user.two_factor_secret.decode('utf-8'))
    valid_code = codeqr.now()
    post_response = test_client.post('/settings/2fa/enable', data={"code": valid_code}, follow_redirects=True)
    assert post_response.status_code == 200
    assert post_response.request.path == '/'


def test_enable_two_factor_get_shows_qr_and_secret(test_client, clean_database):
    logout(test_client)
    user = User(email="enable_get@example.com", password="testpass123", two_factor_enabled=False)
    db.session.add(user)
    db.session.commit()

    login(test_client, "enable_get@example.com", "testpass123")

    response = test_client.get('/settings/2fa/enable')

    assert response.status_code == 200
    assert b"data:image/png;base64," in response.data
    stored = UserRepository().get_by_email("enable_get@example.com")
    assert stored.two_factor_secret is not None


def test_enable_two_factor_post_success(test_client, clean_database):
    logout(test_client)
    user = User(email="enable_post@example.com", password="testpass123", two_factor_enabled=False)
    db.session.add(user)
    db.session.commit()

    resp_login = login(test_client, "enable_post@example.com", "testpass123")
    assert resp_login.status_code == 200
    assert resp_login.request.path != '/login'

    test_client.get('/settings/2fa/enable')

    stored = UserRepository().get_by_email("enable_post@example.com")
    assert stored.two_factor_secret is not None
    secret = stored.two_factor_secret.decode('utf-8')

    totp = pyotp.TOTP(secret)
    good_code = totp.now()

    response_ok = test_client.post('/settings/2fa/enable', data={"code": good_code}, follow_redirects=True)
    assert response_ok.status_code == 200
    assert response_ok.request.path == '/'

    updated = UserRepository().get_by_email("enable_post@example.com")
    assert updated.two_factor_enabled is True


def test_enable_two_factor_post_failure(test_client, clean_database):
    logout(test_client)
    user2 = User(email="enable_post2@example.com", password="testpass123", two_factor_enabled=False)
    db.session.add(user2)
    db.session.commit()

    login(test_client, "enable_post2@example.com", "testpass123")

    test_client.get('/settings/2fa/enable')

    response_fail = test_client.post('/settings/2fa/enable', data={"code": "000000"}, follow_redirects=True)
    assert response_fail.status_code == 200
    assert response_fail.request.path == '/settings/2fa/enable'


def test_verify_2fa_code_success(test_client, clean_database):
    logout(test_client)
    user = User(email="example@example.com", password="testpass123", two_factor_enabled=True)
    db.session.add(user)
    db.session.commit()

    secret = pyotp.random_base32()
    user.two_factor_secret = secret.encode('utf-8')
    db.session.commit()
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()

    response = test_client.post('/verify-2fa', data={"code": valid_code}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/'


def test_verify_2fa_code_no_user_id(test_client, clean_database):
    logout(test_client)

    response = test_client.post('/verify-2fa', data={"code": "123456"}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'


def test_verify_2fa_code_invalid_user(test_client, clean_database):
    logout(test_client)

    with test_client.session_transaction() as sess:
        sess['temp_user_id'] = 9999

    response = test_client.post('/verify-2fa', data={"code": "123456"}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'


def test_verify_2fa_code_two_factor_disabled(test_client, clean_database):
    logout(test_client)
    user = User(email="example@example.com", password="testpass123", two_factor_enabled=False)
    db.session.add(user)
    db.session.commit()

    response = test_client.post('/verify-2fa', data={"code": "123456"}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'


def test_verify_2fa_code_failure(test_client, clean_database):
    logout(test_client)
    user = User(email="example@example.com", password="testpass123", two_factor_enabled=True)
    db.session.add(user)
    db.session.commit()
    secret = pyotp.random_base32()
    user.two_factor_secret = secret.encode('utf-8')
    db.session.commit()

    invalid_code = "000000"
    response = test_client.post('/verify-2fa', data={"code": invalid_code}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'


def test_verify_2fa_code_invalid_code_shows_flash(test_client, clean_database):
    logout(test_client)

    user = User(email="flash@example.com", password="testpass123", two_factor_enabled=True)
    db.session.add(user)
    db.session.commit()

    secret = pyotp.random_base32()
    user.two_factor_secret = secret.encode('utf-8')
    db.session.commit()

    with test_client.session_transaction() as sess:
        sess['temp_user_id'] = user.id

    response = test_client.post('/verify-2fa', data={"code": "000000"}, follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/verify-2fa'
    assert "Código 2FA incorrecto.".encode('utf-8') in response.data or b"2FA incorrecto" in response.data

    with test_client.session_transaction() as sess:
        assert sess.get('temp_user_id') == user.id
