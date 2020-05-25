from __future__ import annotations

import logging
from typing import Optional

import requests
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from polemicflow.common.forms import AssignUserMixin

from .models import Entry, EntrySet, Reply

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

    def clean_url(self):
        url = self.cleaned_data["url"]

        if url == self.instance.url:
            logger.debug("Skiped entry url clean, because url didn't change")
            return url

        try:
            with requests.Session() as session:
                session.max_redirects = 2
                response = session.head(
                    url, allow_redirects=True, timeout=settings.DEFAULT_REQUESTS_TIMEOUT
                )
        except requests.RequestException:
            raise ValidationError(
                _("Could not reach target url: %(url)s"),
                code="inaccessible",
                params={"url": url},
            )

        return response.url


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
    extra=0,
    can_delete=False,
)


class ReplyForm(AssignUserMixin[Reply], forms.ModelForm):
    user_field_name = "author"

    class Meta:
        model = Reply
        fields = ["parent", "text"]

    def __init__(self, *args, entryset: Optional[EntrySet] = None, **kwargs):
        if entryset is None:
            raise ValueError("Entry set must be specified.")

        self.entryset = entryset
        super().__init__(*args, **kwargs)

    def save(self, commit: bool = True) -> Reply:
        self.instance.set = self.entryset
        return super().save(commit=commit)
