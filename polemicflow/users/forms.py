from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm as DjangoAuthenticationForm,
    UserCreationForm as DjangoUserCreationForm,
)

from polemicflow.common.forms import UniqueAutoIdMixin


class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "password1", "password2"]


class AuthenticationForm(UniqueAutoIdMixin, DjangoAuthenticationForm):
    """
    Polemicflow authentication form
    """
