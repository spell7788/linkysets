from __future__ import annotations

import cgi
import logging

import requests
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from polemicflow.common.forms import AssignUserMixin

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
                type_ = self.instance.determine_type(mime_type)
                cleaned_data = {**cleaned_data, "type": type_}
                logger.debug(
                    'Entry type got updated to "%s"',
                    Entry.EntryType(type_).label,  # type: ignore
                )

        return cleaned_data


class EntryInlineFormsetBase(BaseInlineFormSet):
    def __init__(self, *args, is_update: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_delete = is_update


EntryInlineFormset = inlineformset_factory(
    EntrySet,
    Entry,
    form=EntryForm,
    formset=EntryInlineFormsetBase,
    min_num=1,
    validate_min=True,
    extra=1,
    can_delete=False,
)
