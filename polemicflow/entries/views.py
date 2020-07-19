# flake8: noqa: W503
from __future__ import annotations

import logging
from typing import Any

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .forms import EntryFormset, EntrySetForm, SearchForm
from .managers import EntrySetQuerySet
from .models import Entry, EntrySet

logger = logging.getLogger(__name__)


class HomeView(ListView):
    queryset = EntrySet.objects.num_entries().num_replies()
    template_name = "entries/home.html"
    ordering = "created"
    paginate_by = 10


class SearchView(ListView):
    template_name = "entries/search.html"
    paginate_by = 10

    form: SearchForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.form = SearchForm(request.GET or None, initial=request.GET)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context

    def get_queryset(self) -> EntrySetQuerySet[EntrySet]:
        if not self.form.is_valid():
            return EntrySet.objects.none()

        term = self.form.cleaned_data.get("term")
        qs = EntrySet.objects.all().num_entries().num_replies()
        qs = qs.filter(
            Q(name__unaccent__lower__trigram_similar=term)
            | Q(author__username__icontains=term)
            | Q(entries__label__unaccent__lower__trigram_similar=term)
            | Q(entries__url__icontains=term)
        )
        qs = qs.order_by("created").distinct()
        return qs


def create_entryset_view(request: HttpRequest) -> HttpResponse:
    user = request.user if request.user.is_authenticated else None
    form = EntrySetForm(request.POST or None, user=user)
    formset = EntryFormset(request.POST or None)

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():  # type: ignore
            with transaction.atomic():
                entryset = form.save()
                formset.instance = entryset
                saved_entries = formset.save()
                entryset.entries.set(saved_entries)

            logger.debug(
                'Entryset has been created: "%s". Entries: %s',
                entryset,
                ", ".join(str(entry) for entry in entryset.entries.all()),
            )
            messages.success(request, _("Set has been successfully created."))
            return redirect("entries:home")

    context = {
        "form": form,
        "formset": formset,
        "hero_title": _("Create set"),
        "submit_text": _("Create"),
    }
    return render(request, "entries/entryset_form.html", context)


def edit_entryset_view(request: HttpRequest, pk: Any) -> HttpResponse:
    entryset = get_object_or_404(EntrySet, pk=pk)
    form = EntrySetForm(request.POST or None, instance=entryset)
    formset = EntryFormset(request.POST or None, instance=entryset)

    if request.method == "POST":
        updated = False
        if form.has_changed() and form.is_valid():
            entryset = form.save()
            updated = True

        if formset.is_valid():  # type: ignore
            saved_entries = formset.save(commit=False)

            entryset.entries.remove(*formset.deleted_objects)
            for entry in formset.deleted_objects:
                entry.delete()

            for entry in saved_entries:
                entry.save()
            entryset.entries.add(*saved_entries)

            logger.debug(
                "Entry formset saved entries: %s. Deleted entries: %s",
                saved_entries,
                formset.deleted_objects,
            )
            updated = True

        if updated:
            messages.success(request, _("Set has been successfully edited."))
            return redirect("entries:home")

    context = {
        "form": form,
        "formset": formset,
        "hero_title": _("Edit set"),
        "submit_text": _("Confirm"),
    }
    return render(request, "entries/entryset_form.html", context)


class EntrySetDetailView(DetailView):
    queryset = EntrySet.objects.num_entries().num_replies().prefetch_replies()
    template_name = "entries/entryset_detail.html"


@require_POST
def repost_entry_view(request: HttpRequest, pk: Any) -> HttpResponse:
    if Entry.objects.filter(pk=pk).exists():
        with transaction.atomic():
            entryset = EntrySet.objects.create()
            entryset.entries.add(pk)
    else:
        raise Http404(f"No {Entry._meta.object_name} matches the given query.")

    return redirect("entries:edit", pk=entryset.pk)
