from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from common.constants import USERS_PER_PAGE
from common.services import get_query_prefix, paginate_queryset

from .forms import LoginForm, ProfileForm, RegisterForm
from .services import (
    change_password_and_keep_session,
    login_form_user,
    logout_current_user,
    public_profiles,
    register_and_login,
    save_profile_form,
)


User = get_user_model()


def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        register_and_login(request, form)
        return redirect("projects:project_list")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None, request=request)

    if form.is_valid():
        login_form_user(request, form)
        return redirect("projects:project_list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout_current_user(request)
    return redirect("projects:project_list")


def profile_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id, is_active=True)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)

    if form.is_valid():
        save_profile_form(form)
        return redirect("users:profile_detail", user_id=request.user.id)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if form.is_valid():
        change_password_and_keep_session(request, form)
        return redirect("users:profile_detail", user_id=request.user.id)

    return render(request, "users/change_password.html", {"form": form})


def participants(request):
    page = paginate_queryset(request, public_profiles(), USERS_PER_PAGE)
    return render(
        request,
        "users/participants.html",
        {"participants": page, "page_obj": page, "query_prefix": get_query_prefix(request)},
    )

