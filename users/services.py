import re

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth import get_user_model


PHONE_RE = re.compile(r"^(?:8|\+7)\d{10}$")


def clean_phone_string(value):
    if not value:
        return ""
    return value.strip().replace(" ", "").replace("-", "")


def normalize_phone(value):
    phone = clean_phone_string(value)
    if not phone:
        return None

    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


def is_valid_phone(value):
    return bool(PHONE_RE.match(clean_phone_string(value)))


def register_and_login(request, form):
    user = form.save()
    login(request, user)
    return user


def login_form_user(request, form):
    login(request, form.user)


def logout_current_user(request):
    logout(request)


def save_profile_form(form):
    return form.save()


def change_password_and_keep_session(request, form):
    form.save()
    update_session_auth_hash(request, request.user)


def public_profiles():
    User = get_user_model()
    return User.objects.filter(is_active=True).order_by("-date_joined")
