from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional, Sequence, cast
from urllib.parse import parse_qs, urlsplit

from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.functional import cached_property

if TYPE_CHECKING:
    from .models import Entry

logger = logging.getLogger(__name__)


class EntryTypeBehavior:
    mime_types: ClassVar[Optional[Sequence[str]]] = None
    template_name: ClassVar[Optional[str]] = None
    template_string: ClassVar[Optional[str]] = None

    entry: Entry

    def __init__(self, entry: Entry):
        self.entry = entry

    @classmethod
    def is_my_type(cls, entry: Entry, url: str, mime_type: str, *args, **kwargs) -> bool:
        if not cls.mime_types:
            return False
        return mime_type in cls.mime_types

    def render(self) -> str:
        if not self.template_string and not self.template_name:
            raise AttributeError('Either "template_string" or "template_name" is required.')

        context_dict = self.get_render_context()
        if self.template_name:
            return render_to_string(self.template_name, context_dict)

        context = Context(context_dict)
        template_string = cast(str, self.template_string)
        return Template(template_string).render(context)

    def get_render_context(self) -> Dict[str, Any]:
        return {"entry": self.entry}


class UrlTypeBehavior(EntryTypeBehavior):
    template_string = """
        <a href="{{ entry.url }}" target="_blank">
            {% if entry.label %}{{ entry.label }}{% else %}{{ entry.url }}{% endif %}
        </a>
    """

    @classmethod
    def is_my_type(cls, *args, **kwargs) -> bool:
        return True


class ImageTypeBehavior(EntryTypeBehavior):
    template_string = """
        <img src="{{ entry.url }}" alt="{{ entry.label }}">
    """
    mime_types = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    ]


class VideoTypeBehavior(EntryTypeBehavior):
    mime_types = [
        "video/mp4",
        "video/webm",
        "video/ogg",
    ]
    template_name = "entries/types/video.html"


class AudioBehavior(EntryTypeBehavior):
    mime_types = [
        "audio/wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/aac",
        "audio/aacp",
        "audio/ogg",
        "audio/webm",
        "audio/flac",
    ]
    template_name = "entries/types/audio.html"


class YtVideoTypeBehavior(EntryTypeBehavior):
    mime_types = ["text/html"]
    template_name = "entries/types/yt_video.html"

    YT_NETLOC_VARIANTS: ClassVar[Sequence[str]] = [
        "www.youtube.com",
        "youtube.com",
        "youtu.be",
    ]

    @classmethod
    def is_my_type(cls, entry: Entry, url: str, mime_type: str, *args, **kwargs) -> bool:
        netloc = urlsplit(url).netloc
        logger.debug('Youtube url network location: "%s"', netloc)
        is_my_mime_type = super().is_my_type(entry, url, mime_type, *args, **kwargs)
        return is_my_mime_type and netloc in cls.YT_NETLOC_VARIANTS

    def get_render_context(self):
        context = super().get_render_context()
        context = {**context, "embed_url": self.embed_url}
        return context

    @cached_property
    def embed_url(self) -> str:
        parsed_url = urlsplit(self.entry.url)
        query_string = parsed_url.query
        try:
            video_id, *_ = parse_qs(query_string)["v"]
        except KeyError:
            video_id = parsed_url.path.split("/")[-1]

        logger.debug(
            'YT video url: "%s". Parsed url: "%s". video id: "%s"',
            self.entry.url,
            parsed_url,
            video_id,
        )
        return f"https://www.youtube.com/embed/{video_id}"
