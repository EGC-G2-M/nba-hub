from flask import redirect, render_template, request, url_for, session, flash
from flask_login import current_user, login_user, logout_user, login_required

from app.modules.auth import auth_bp
from app.modules.auth.forms import LoginForm, SignupForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form,
                                   error=f"Email {email} in use")

        try:
            user = authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form,
                                   error=f"Error creating user: {exc}")

        # Log user
        login_user(user, remember=True)
        return redirect(url_for("public.index"))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = authentication_service.check_credentials(email, password)

        if user:
            if user.two_factor_enabled:
                # 2FA Habilitado: Redirigir a verificación
                session['temp_user_id'] = user.id
                flash("Introduce tu código de autenticación de dos factores.", "info")
                return redirect(url_for("auth.verify_2fa_code"))
            else:
                # 2FA Deshabilitado: Login normal
                authentication_service.login(user)
                return redirect(url_for("public.index"))

        # Credenciales inválidas
        return render_template("auth/login_form.html", form=form,
                               error="Invalid credentials")

    return render_template("auth/login_form.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))


@auth_bp.route('/settings/2fa/enable', methods=['GET', 'POST'])
@login_required
def enable_two_factor():
    # Evitar que se active si ya está habilitado
    if current_user.two_factor_enabled:
        flash("La autenticación de dos factores ya está habilitada.", "info")
        return redirect(url_for("public.index"))

    if request.method == 'GET':
        secret, uri, qr_base64 = authentication_service.generate_2fa_setup(current_user)

        return render_template('auth/2fa_enable.html',
                               qr_base64=qr_base64, secret=secret)

    elif request.method == 'POST':
        code = request.form.get('code')

        if authentication_service.verify_and_enable_2fa(current_user, code):
            flash("2FA habilitado con éxito.", "success")
            return redirect(url_for("public.index"))
        else:
            flash("Código 2FA incorrecto. Intenta de nuevo.", "warning")
            return redirect(url_for('auth.enable_two_factor'))


@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa_code():
    user_id = session.get('temp_user_id')

    if not user_id:
        return redirect(url_for('auth.login'))

    user = authentication_service.repository.get_by_id(user_id)

    if not user or not user.two_factor_enabled:
        session.pop('temp_user_id', None)
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code = request.form.get('code')

        if authentication_service.verify_2fa_code(user, code):
            session.pop('temp_user_id', None)
            authentication_service.login(user)
            flash("Autenticación de dos factores exitosa.", "success")
            return redirect(url_for('public.index'))
        else:
            flash("Código 2FA incorrecto.", "warning")

    return render_template('auth/verify_2fa_form.html', email=user.email)
