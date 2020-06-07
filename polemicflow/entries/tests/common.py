import random
import string

from requests import Response

from ..behavior import YtVideoTypeBehavior


def get_mock_response(url: str, content_type: str):
    response = Response()
    response.url = url
    response.headers["content-type"] = content_type
    return response


_ASCII_LETTERS_AND_DIGITS = string.ascii_letters + string.digits


def get_random_youtube_url() -> str:
    netloc = random.choice(YtVideoTypeBehavior.YT_NETLOC_VARIANTS)
    id_length = random.randint(6, 12)
    video_id = "".join(random.choice(_ASCII_LETTERS_AND_DIGITS) for _ in range(id_length))
    if netloc == "youtu.be":
        return f"https://{netloc}/{video_id}"
    return f"https://{netloc}/watch?v={video_id}"
