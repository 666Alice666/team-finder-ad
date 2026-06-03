from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm, ReadOnlyPasswordHashField

from common.constants import USER_NAME_MAX_LENGTH, USER_SURNAME_MAX_LENGTH
from common.forms import validate_github_url

from .models import User
from .services import is_valid_phone, normalize_phone


class RegisterForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=USER_NAME_MAX_LENGTH)
    surname = forms.CharField(label="Фамилия", max_length=USER_SURNAME_MAX_LENGTH)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self):
        return User.objects.create_user(**self.cleaned_data)


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user = authenticate(
                self.request,
                username=email.lower(),
                password=password,
            )
            if self.user is None:
                raise forms.ValidationError("Неверный имейл или пароль")

        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        raw_phone = self.cleaned_data.get("phone")
        if not raw_phone:
            return None

        if not is_valid_phone(raw_phone):
            raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")

        normalized = normalize_phone(raw_phone)
        duplicate = User.objects.filter(phone=normalized)
        if self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)

        if duplicate.exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует.")

        return normalized

    def clean_github_url(self):
        value = self.cleaned_data.get("github_url")
        validate_github_url(value)
        return value


class UserPasswordChangeForm(PasswordChangeForm):
    pass


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "name", "surname")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminUserChangeForm(ProfileForm):
    password = ReadOnlyPasswordHashField(label="Пароль")

    class Meta(ProfileForm.Meta):
        fields = ProfileForm.Meta.fields + [
            "email",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        ]

