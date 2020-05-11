from typing import TYPE_CHECKING, Dict, Union

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import AnonymousUser
from django.forms import Form
from django.http import HttpRequest

if TYPE_CHECKING:
    from .models import User


def login(request: HttpRequest) -> Dict[str, Form]:
    user: Union[User, AnonymousUser] = request.user
    if user.is_authenticated:
        return {}

    return {"login_form": AuthenticationForm(request)}
