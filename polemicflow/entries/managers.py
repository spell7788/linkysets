from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.db.models import Count, Manager, OuterRef, Prefetch, QuerySet, Subquery

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

    def prefetch_entries(self) -> EntrySetQuerySet[EntrySet]:
        Entry = apps.get_model("entries.Entry")
        # Annotate entry sets count in prefetch subquery
        # https://stackoverflow.com/a/44474268/10079612
        m2m_model = Entry.sets.through
        m2m_qs = m2m_model.objects.filter(entry=OuterRef("pk")).values("pk")
        num_of_sets_qs = m2m_qs.annotate(num_of_sets=Count("*")).values("num_of_sets")
        num_of_sets_qs.query.group_by = []

        qs = Entry.objects.annotate(num_of_sets=Subquery(num_of_sets_qs))
        qs = qs.select_related("origin")
        return self.prefetch_related(Prefetch("entries", queryset=qs))

    def prefetch_replies(self) -> EntrySetQuerySet[EntrySet]:
        Reply = apps.get_model("replies.Reply")
        return self.prefetch_related(
            Prefetch("replies", queryset=Reply.objects.select_related("author"))
        )


class EntrySetManager(EntrySetManagerBase):
    def get_queryset(self) -> EntrySetQuerySet[EntrySet]:
        qs = super().get_queryset()
        qs = qs.select_related("author")
        qs = qs.prefetch_entries()
        qs = qs.num_entries().num_replies()
        return qs
