from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.db.models import Count, Manager, Prefetch, QuerySet

if TYPE_CHECKING:
    from .models import EntrySet

    EntrySetQuerySetBase = QuerySet[EntrySet]
    EntrySetManagerBase = Manager[EntrySet]
else:
    EntrySetQuerySetBase = QuerySet
    EntrySetManagerBase = Manager


class EntrySetQuerySet(EntrySetQuerySetBase):
    def num_entries(self) -> EntrySetQuerySet[EntrySet]:
        return self.annotate(num_entries=Count("entries"))

    def num_replies(self) -> EntrySetQuerySet[EntrySet]:
        return self.annotate(num_replies=Count("replies"))

    def prefetch_replies(self) -> EntrySetQuerySet[EntrySet]:
        Reply = apps.get_model("replies.Reply")
        return self.prefetch_related(
            Prefetch("replies", queryset=Reply.objects.select_related("author"))
        )


class EntrySetManager(EntrySetManagerBase):
    def get_queryset(self) -> EntrySetQuerySet[EntrySet]:
        qs = super().get_queryset()
        qs = qs.select_related("author")
        qs = qs.prefetch_related("entries")
        return qs
