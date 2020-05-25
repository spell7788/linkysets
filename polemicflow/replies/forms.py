from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django import forms

from polemicflow.common.forms import AssignUserMixin

from .models import Reply

if TYPE_CHECKING:
    from polemicflow.entries.models import EntrySet


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
