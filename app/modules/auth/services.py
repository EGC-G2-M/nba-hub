import os

import qrcode
import pyotp
import base64
import io

from flask_login import login_user, current_user

from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.profile.models import UserProfile
from app.modules.profile.repositories import UserProfileRepository
from core.configuration.configuration import uploads_folder_name
from core.services.BaseService import BaseService


class AuthenticationService(BaseService):
    def __init__(self):
        super().__init__(UserRepository())
        self.user_profile_repository = UserProfileRepository()

    def login(self, user: User, remember=True) -> bool:
        # Simplificamos el login una vez que ya verificamos credenciales y 2FA
        if user is not None:
            login_user(user, remember=remember)
            return True
        return False

    # El método login original se modifica para aceptar un objeto User
    # El chequeo de password se mueve a check_credentials (NUEVO)
    def login_initial(self, email, password, remember=True):
        user = self.repository.get_by_email(email)
        if user is not None and user.check_password(password):
            # Aquí la ruta debe decidir si es necesario 2FA
            login_user(user, remember=remember)
            return True
        return False

    def is_email_available(self, email: str) -> bool:
        return self.repository.get_by_email(email) is None

    def create_with_profile(self, **kwargs):
        try:
            email = kwargs.pop("email", None)
            password = kwargs.pop("password", None)
            name = kwargs.pop("name", None)
            surname = kwargs.pop("surname", None)

            if not email:
                raise ValueError("Email is required.")
            if not password:
                raise ValueError("Password is required.")
            if not name:
                raise ValueError("Name is required.")
            if not surname:
                raise ValueError("Surname is required.")

            user_data = {"email": email, "password": password}

            profile_data = {
                "name": name,
                "surname": surname,
            }

            user = self.create(commit=False, **user_data)
            self.repository.session.flush()
            profile_data["user_id"] = user.id
            self.user_profile_repository.create(**profile_data)
            self.repository.session.commit()
            return user
        except Exception as exc:
            self.repository.session.rollback()
            raise exc

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updated_instance = self.update(user_profile_id, **form.data)
            return updated_instance, None

        return None, form.errors

    def get_authenticated_user(self) -> User | None:
        if current_user.is_authenticated:
            return current_user
        return None

    def get_authenticated_user_profile(self) -> UserProfile | None:
        if current_user.is_authenticated:
            return current_user.profile
        return None

    def temp_folder_by_user(self, user: User) -> str:
        return os.path.join(uploads_folder_name(), "temp", str(user.id))

    def save_user_changes(self, user: User) -> User:
        return self.repository.save_changes(user)

    def check_credentials(self, email, password) -> User | None:
        user = self.repository.get_by_email(email)
        if user is not None and user.check_password(password):
            return user
        return None

    def encode_qr_code(self, totp_uri):
        # Genera un código QR a partir de la URI y lo devuelve codificado
        # en Base64
        img = qrcode.make(totp_uri)
        buf = io.BytesIO()  # Crea el objeto QR
        img.save(buf, 'PNG')
        buf.seek(0)
        qr_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return qr_base64

    def verify_and_enable_2fa(self, user: User, code: str) -> bool:
        if not user.two_factor_secret:
            return False

        secret = user.two_factor_secret.decode('utf-8')
        totp = pyotp.TOTP(secret)

        if totp.verify(code):
            user.two_factor_enabled = True
            self.save_user_changes(user)
            return True
        return False

    def verify_2fa_code(self, user: User, code: str) -> bool:
        if not user.two_factor_enabled or not user.two_factor_secret:
            return False

        secret = user.two_factor_secret.decode('utf-8')
        totp = pyotp.TOTP(secret)

        return totp.verify(code)

    def generate_2fa_setup(self, user: User,
                           app_name: str = "NBA Hub") -> tuple[str, str, str]:
        secret = pyotp.random_base32()

        user.two_factor_secret = secret.encode('utf-8')
        self.save_user_changes(user)

        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=app_name
        )

        qr_base64 = self.encode_qr_code(totp_uri)

        return secret, totp_uri, qr_base64
