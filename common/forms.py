from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_github_url(value):
    if not value:
        return

    host = urlparse(value).netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if host != "github.com":
        raise ValidationError("Ссылка должна вести на GitHub.")

