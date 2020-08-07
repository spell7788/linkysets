from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django import forms

from linkysets.common.forms import AssignUserMixin

from .models import Reply

if TYPE_CHECKING:
    from linkysets.entries.models import EntrySet


class ReplyForm(AssignUserMixin[Reply], forms.ModelForm):
    user_field_name = "author"

    class Meta:
        model = Reply
        fields = ["parent", "text"]
        widgets = {
            "parent": forms.HiddenInput(),
        }

    def __init__(self, *args, entryset: Optional[EntrySet] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entryset = entryset

    def save(self, commit: bool = True) -> Reply:
        if self.entryset is None:
            raise ValueError("Entryset is required.")

        self.instance.entryset = self.entryset
        return super().save(commit=commit)
