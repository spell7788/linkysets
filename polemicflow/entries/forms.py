from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import requests
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Entry

if TYPE_CHECKING:
    from polemicflow.users.models import User


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["url"]

    def __init__(self, user: Optional[User] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit: bool = True):
        if self.user is not None:
            self.instance._author = self.user
        return super().save(commit)

    def clean_url(self):
        url = self.cleaned_data["url"]
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
