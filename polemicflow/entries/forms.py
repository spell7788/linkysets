from __future__ import annotations

import cgi
import itertools
import logging
from typing import Sequence

import requests
from django import forms
from django.conf import settings
from django.db.models import QuerySet
from django.forms import BaseInlineFormSet, ValidationError, inlineformset_factory
from django.forms.formsets import DELETION_FIELD_NAME
from django.utils.translation import ugettext_lazy as _

from polemicflow.common.forms import AssignUserMixin, UniqueAutoIdMixin

from .models import Entry, EntrySet

logger = logging.getLogger(__name__)


class EntrySetForm(AssignUserMixin[EntrySet], forms.ModelForm):
    user_field_name = "author"

    class Meta:
        model = EntrySet
        fields = ["name"]


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["type", "url", "label"]
        widgets = {
            "type": forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get("url")
        if not url:
            return cleaned_data

        if url != self.instance.url:
            try:
                with requests.Session() as session:
                    session.max_redirects = 2
                    response = session.head(
                        url, allow_redirects=True, timeout=settings.DEFAULT_REQUESTS_TIMEOUT
                    )
            except requests.RequestException:
                validation_error = ValidationError(
                    _("Could not reach target url: %(url)s"),
                    code="inaccessible_url",
                    params={"url": url},
                )
                self.add_error("url", validation_error)
            else:
                url = response.url
                cleaned_data = {**cleaned_data, "url": url}
                logger.debug('Entry url got tested to "%s"', url)

                mime_type, params = cgi.parse_header(response.headers["content-type"])
                logger.debug(
                    '"%s" mime type is "%s". Parameters: %s', url, mime_type, params,
                )
                type_ = self.instance.determine_type(url, mime_type)
                cleaned_data = {**cleaned_data, "type": type_}
                logger.debug(
                    'Entry type got updated to "%s"',
                    Entry.EntryType(type_).label,  # type: ignore
                )

        return cleaned_data


class EntryFormsetBase(BaseInlineFormSet):
    def clean(self):
        active_forms = [form for form in self.forms if form not in self.deleted_forms]

        urls = (form.cleaned_data.get("url") for form in active_forms if form.cleaned_data)
        urls = (url for url in urls if url)
        for url, other in itertools.combinations(urls, 2):
            if url == other:
                raise ValidationError(
                    _("Entries urls must be unique in one set."), code="unique_entries"
                )

    def save(self, commit: bool = True) -> Sequence[Entry]:
        entries = (form.instance for form in self.forms)
        for entry in entries:
            if entry._state.adding and entry.origin is None:
                entry.origin = self.instance

        return super().save(commit)

    def get_queryset(self) -> QuerySet[Entry]:
        if not self.instance.pk:
            model = type(self.instance)
            return model._default_manager.none()

        qs = self.instance.entries.all()
        if not qs.ordered:
            qs = qs.order_by(self.model._meta.pk.name)

        return qs

    def add_fields(self, form: forms.Form, index: int) -> None:
        super().add_fields(form, index)
        if self.can_delete:
            form.fields[DELETION_FIELD_NAME].widget = forms.HiddenInput()

    @classmethod
    def get_default_prefix(cls) -> str:
        return "entries"


EntryFormset = inlineformset_factory(
    EntrySet,
    Entry,
    form=EntryForm,
    formset=EntryFormsetBase,
    min_num=1,
    validate_min=True,
    extra=0,
)


class SearchForm(UniqueAutoIdMixin, forms.Form):
    term = forms.CharField(max_length=100, label=_("Term"), help_text=_("Search term"))
