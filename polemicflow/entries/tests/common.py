from __future__ import annotations

import random
import string
from typing import TYPE_CHECKING, Any, Callable, Dict, Sequence

from faker import Faker
from requests import Response

from ..behavior import YtVideoTypeBehavior
from ..forms import EntryFormset

if TYPE_CHECKING:
    from ..models import EntrySet


def head_response_factory(
    get_content_type: Callable[Response, str] = lambda response: "text/html; charset=utf-8",
):
    def get_response(url: str, *args, **kwargs) -> Response:
        response = Response()
        response.url = url
        response.headers["content-type"] = get_content_type(response)
        return response

    return get_response


_ASCII_LETTERS_AND_DIGITS = string.ascii_letters + string.digits


def get_random_youtube_url() -> str:
    netloc = random.choice(YtVideoTypeBehavior.YT_NETLOC_VARIANTS)
    id_length = random.randint(6, 12)
    video_id = "".join(random.choice(_ASCII_LETTERS_AND_DIGITS) for _ in range(id_length))
    if netloc == "youtu.be":
        return f"https://{netloc}/{video_id}"
    return f"https://{netloc}/watch?v={video_id}"


_fake = Faker()


class EntryFormsetDataMixin:
    _FORMSET_PREFIX = EntryFormset.get_default_prefix()

    def get_random_data(self, forms_num: int = 1) -> Dict[str, Any]:
        data = {
            f"{self._FORMSET_PREFIX}-TOTAL_FORMS": forms_num,
            f"{self._FORMSET_PREFIX}-INITIAL_FORMS": forms_num,
        }
        for i in range(forms_num):
            url_field, label_field = self._generate_field_names(i, ["url", "label"])
            data = {**data, url_field: _fake.url(), label_field: _fake.pystr()}

        return data

    def get_data_from_entryset(self, entryset: EntrySet) -> Dict[str, Any]:
        entries = entryset.entries.all()
        entries_length = len(entries)
        data = {
            f"{self._FORMSET_PREFIX}-TOTAL_FORMS": entries_length,
            f"{self._FORMSET_PREFIX}-INITIAL_FORMS": entries_length,
        }
        for i, entry in enumerate(entries):
            id_field, url_field, label_field = self._generate_field_names(
                i, ["id", "url", "label"]
            )
            data = {
                **data,
                id_field: entry.id,
                url_field: entry.url,
                label_field: entry.label,
            }

        return data

    def _generate_field_names(
        self, form_index: int, fields: Sequence[str]
    ) -> Sequence[str]:
        return [f"{self._FORMSET_PREFIX}-{form_index}-{field}" for field in fields]
