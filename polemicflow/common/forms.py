from typing import Any, Generic, Optional, TypeVar

from django.db.models import Model

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
