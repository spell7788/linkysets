from typing import Any, Generic, Optional, TypeVar, Union

from django.db.models import Model
from django.utils.crypto import get_random_string

I = TypeVar("I", bound=Model)  # noqa: E741

_MISSING = object()


class AssignUserMixin(Generic[I]):
    instance: I
    user_field_name: str = "user"

    def __init__(self, *args, user: Optional[Any] = _MISSING, **kwargs):
        super().__init__(*args, **kwargs)  # type: ignore
        self.user = user

    def save(self, commit: bool = True) -> I:  # noqa: E741
        if not hasattr(self.instance, self.user_field_name):
            raise ValueError(
                f'"{type(self.instance).__name__}" '
                f'does not have user field with a name "{self.user_field_name}".'
            )

        if self.user is not _MISSING:
            setattr(self.instance, self.user_field_name, self.user)

        return super().save(commit)  # type: ignore


class UniqueAutoIdMixin:
    _auto_id: Union[bool, str]

    @property
    def auto_id(self) -> Union[bool, str]:
        if isinstance(self._auto_id, bool):
            return self._auto_id

        unique_suffix = get_random_string(6)
        return f"{self._auto_id}_{unique_suffix}"

    @auto_id.setter
    def auto_id(self, auto_id: Union[bool, str]) -> None:
        self._auto_id = auto_id
