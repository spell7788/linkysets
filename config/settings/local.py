from .base import *  # noqa

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405

DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}
