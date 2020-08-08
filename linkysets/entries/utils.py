from django.conf import settings
from django.utils.text import format_lazy


def join_page_title(title: str) -> str:
    sep = settings.PAGE_TITLE_SEPARATOR
    ext = settings.PAGE_TITLE_EXTENSION
    return format_lazy(
        "{title} {separator} {extension}", title=title, separator=sep, extension=ext
    )
