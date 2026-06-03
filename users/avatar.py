from hashlib import blake2b
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from common.constants import (
    AVATAR_FORMAT,
    AVATAR_FONT_NAME,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
)

AVATAR_BACKGROUND_LIGHTNESS = 150
AVATAR_BACKGROUND_RANGE = 70
AVATAR_FONT_SCALE = 0.58


def build_initial_avatar(*, email, name, surname):
    initials = get_initials(name, surname, email)
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color_from_identity(email, name, surname))
    drawer = ImageDraw.Draw(image)
    font = load_avatar_font()
    text_box = drawer.textbbox((0, 0), initials, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    position = (
        (AVATAR_SIZE - text_width) / 2 - text_box[0],
        (AVATAR_SIZE - text_height) / 2 - text_box[1],
    )
    drawer.text(position, initials, fill=AVATAR_TEXT_COLOR, font=font)

    output = BytesIO()
    image.save(output, format=AVATAR_FORMAT)
    return ContentFile(output.getvalue())


def get_initials(name, surname, email):
    first = (name or email or "?").strip()[:1]
    second = (surname or "").strip()[:1]
    return f"{first}{second}".upper()


def color_from_identity(*parts):
    digest = blake2b("|".join(part or "" for part in parts).encode(), digest_size=3).digest()
    return tuple(AVATAR_BACKGROUND_LIGHTNESS + channel % AVATAR_BACKGROUND_RANGE for channel in digest)


def load_avatar_font():
    font_size = int(AVATAR_SIZE * AVATAR_FONT_SCALE)
    try:
        return ImageFont.truetype(AVATAR_FONT_NAME, font_size)
    except OSError:
        return ImageFont.load_default(size=font_size)
