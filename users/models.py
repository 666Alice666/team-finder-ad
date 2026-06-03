from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from common.constants import (
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)

from .avatar import build_initial_avatar
from .managers import UserManager


def avatar_path(instance, filename):
    return f"avatars/user_{instance.pk or 'new'}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email", unique=True)
    name = models.CharField("имя", max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField("фамилия", max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField("аватар", upload_to=avatar_path, blank=True)
    phone = models.CharField(
        "телефон",
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
    )
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("о себе", max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField("активен", default=True)
    is_staff = models.BooleanField("администратор", default=False)
    date_joined = models.DateTimeField("дата регистрации", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.name} {self.surname} <{self.email}>"

    def save(self, *args, **kwargs):
        create_avatar = not self.avatar or not self.avatar.storage.exists(self.avatar.name)
        super().save(*args, **kwargs)

        if create_avatar:
            self.avatar.save(
                f"avatar_{self.pk}.png",
                build_initial_avatar(
                    email=self.email,
                    name=self.name,
                    surname=self.surname,
                ),
                save=False,
            )
            super().save(update_fields=["avatar"])

