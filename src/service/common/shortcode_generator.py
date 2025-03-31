import random
import string

from service.core.config import settings


def generate_short_code(length: int = None) -> str:
    """Generate a random short code for a URL"""
    if length is None:
        length = settings.SHORT_CODE_LENGTH

    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))
