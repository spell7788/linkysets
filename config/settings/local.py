# flake8: noqa
from typing import Any

from .base import *

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += [
    "polemicflow.common.middleware.random_debug_message",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}

LOGGING["loggers"]["polemicflow"]["level"] = "DEBUG"  # type: ignore
