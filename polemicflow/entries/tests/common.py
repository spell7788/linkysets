from unittest.mock import patch

from django.core.exceptions import ValidationError

from ..forms import EntryForm

successful_clean_url_patch = patch.object(
    EntryForm,
    "clean_url",
    side_effect=lambda self: self.cleaned_data["url"],
    autospec=True,
)

failing_clean_url_patch = patch.object(
    EntryForm, "clean_url", side_effect=ValidationError("Could not reach target url"),
)
