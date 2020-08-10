from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm as DjangoAuthenticationForm,
    UserCreationForm as DjangoUserCreationForm,
)

from linkysets.common.forms import UniqueAutoIdMixin


class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "password1", "password2"]


class AuthenticationForm(UniqueAutoIdMixin, DjangoAuthenticationForm):  # type: ignore
    """
    Linkysets authentication form
    """
