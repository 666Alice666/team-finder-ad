from django.conf import settings
from django.db import models

from common.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_MAX_LENGTH,
    PROJECT_STATUS_OPEN,
    SKILL_NAME_MAX_LENGTH,
)


class Skill(models.Model):
    name = models.CharField(
        "название навыка",
        max_length=SKILL_NAME_MAX_LENGTH,
        unique=True,
        db_index=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "навык"
        verbose_name_plural = "навыки"

    def __str__(self):
        return self.name


class Project(models.Model):
    OPEN = PROJECT_STATUS_OPEN
    CLOSED = PROJECT_STATUS_CLOSED
    STATUS_CHOICES = (
        (OPEN, "Open"),
        (CLOSED, "Closed"),
    )

    name = models.CharField("название", max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField("описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="автор",
    )
    created_at = models.DateTimeField("дата создания", auto_now_add=True, db_index=True)
    github_url = models.URLField("GitHub", blank=True)
    status = models.CharField(
        "статус",
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="participated_projects",
        verbose_name="участники",
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="projects",
        verbose_name="необходимые навыки",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]
        verbose_name = "проект"
        verbose_name_plural = "проекты"

    def __str__(self):
        return self.name

    @property
    def is_open(self):
        return self.status == self.OPEN

