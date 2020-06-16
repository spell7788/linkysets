import logging
from typing import Any

from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView

from .forms import EntryFormset, EntrySetForm
from .models import Entry, EntrySet

logger = logging.getLogger(__name__)


class HomeView(ListView):
    model = EntrySet
    template_name = "entries/home.html"


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

    context = {"form": form, "formset": formset}
    return render(request, "entries/entryset_form.html", context)


def update_entryset_view(request: HttpRequest, pk: Any) -> HttpResponse:
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
            messages.success(request, _("Entries set has been successfully updated."))
            return redirect("entries:home")

    context = {"form": form, "formset": formset}
    return render(request, "entries/entryset_form.html", context)


class EntrySetDetailView(DetailView):
    model = EntrySet
    template_name = "entries/entryset_detail.html"
