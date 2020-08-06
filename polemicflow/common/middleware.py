import random
from typing import Callable

from django.conf import settings
from django.contrib import messages
from django.contrib.messages import constants as message_constants
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from django.utils import lorem_ipsum


def random_debug_message(get_response: Callable[..., HttpResponse]):
    if not settings.DEBUG:
        raise MiddlewareNotUsed("Random debug message middleware is only for debugging.")

    MESSAGE_LEVELS = [
        message_constants.DEBUG,
        message_constants.INFO,
        message_constants.SUCCESS,
        message_constants.WARNING,
        message_constants.ERROR,
    ]

    def middleware(request: HttpRequest) -> HttpResponse:
        messages_ = messages.get_messages(request)
        if len(messages_) > 0:
            return get_response(request)

        level = random.choice(MESSAGE_LEVELS)
        message = lorem_ipsum.words(random.randint(6, 12), common=False)
        messages.set_level(request, message_constants.DEBUG)
        messages.add_message(request, level, message)
        return get_response(request)

    return middleware
