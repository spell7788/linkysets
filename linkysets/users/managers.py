from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, QuerySet

if TYPE_CHECKING:
    from .models import User

    BaseUserQuerySet = QuerySet[User]
else:
    BaseUserQuerySet = QuerySet


class UserQuerySet(BaseUserQuerySet):
    def num_entrysets(self) -> UserQuerySet:
        return self.annotate(num_sets=Count("entryset", distinct=True))  # type: ignore

    def num_replies(self) -> UserQuerySet:
        return self.annotate(num_replies=Count("reply", distinct=True))  # type: ignore
