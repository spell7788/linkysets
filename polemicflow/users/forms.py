from typing import Union

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm as DjangoAuthenticationForm,
    UserCreationForm as DjangoUserCreationForm,
)
from django.utils.crypto import get_random_string


class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "password1", "password2"]


class AuthenticationForm(DjangoAuthenticationForm):
    _auto_id: str

    @property
    def auto_id(self) -> str:
        id_ = self._auto_id
        unique_suffix = get_random_string(6)
        return f"{id_}_{unique_suffix}"

    @auto_id.setter
    def auto_id(self, auto_id: Union[bool, str]) -> None:
        self._auto_id = auto_id
