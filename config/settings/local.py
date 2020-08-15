# flake8: noqa: F405
from typing import Any

from .base import *

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += [
    "linkysets.common.middleware.random_debug_message",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}

LOGGING["loggers"]["linkysets"]["level"] = "DEBUG"  # type: ignore
