from typing import TYPE_CHECKING, Dict, Union

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.forms import Form
from django.http import HttpRequest
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from .models import User

AuthenticationForm = import_string(settings.AUTHENTICATION_FORM)


def login(request: HttpRequest) -> Dict[str, Form]:
    user: Union[User, AnonymousUser] = request.user
    if user.is_authenticated:
        return {}

    return {"login_form": AuthenticationForm(request)}
