import logging
from typing import Any, List

from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView

from .forms import EntryInlineFormset, EntrySetForm
from .models import Entry, EntrySet

logger = logging.getLogger(__name__)


class HomeView(ListView):
    model = EntrySet
    template_name = "entries/home.html"


def create_entryset_view(request: HttpRequest) -> HttpResponse:
    user = request.user if request.user.is_authenticated else None
    form = EntrySetForm(request.POST or None, user=user)
    formset = EntryInlineFormset(request.POST or None)

    if request.method == "POST":
        if formset.has_changed() and form.is_valid() and formset.is_valid():  # type: ignore
            with transaction.atomic():
                entryset = form.save()
                uncommited_entries = formset.save(commit=False)

                entries: List[Entry] = []
                for entry in uncommited_entries:
                    entry.origin = entryset
                    entry.save()
                    entries.append(entry)
                entryset.entries.add(*entries)

            logger.debug(
                'Entryset has been created: "%s". Entries: %s',
                entryset,
                ", ".join(map(str, entries)),
            )
            messages.success(request, _("Entries set has been successfully created."))
            return redirect("entries:home")

    context = {"form": form, "formset": formset}
    return render(request, "entries/entryset_form.html", context)


def update_entryset_view(request: HttpRequest, pk: Any) -> HttpResponse:
    entryset = get_object_or_404(EntrySet, pk=pk)
    form = EntrySetForm(request.POST or None, instance=entryset)
    formset = EntryInlineFormset(request.POST or None, instance=entryset, is_update=True)

    if request.method == "POST":
        updated = False
        if form.has_changed() and form.is_valid():
            entryset = form.save()
            updated = True

        if formset.has_changed() and formset.is_valid():  # type: ignore
            entries = formset.save()
            entryset.entries.add(*entries)
            updated = True

        if updated:
            messages.success(request, _("Entries set has been successfully updated."))
        return redirect("entries:home")

    context = {"form": form, "formset": formset}
    return render(request, "entries/entryset_form.html", context)
