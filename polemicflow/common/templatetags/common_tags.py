from typing import Optional

from django import template
from django.http import HttpRequest

register = template.Library()


@register.simple_tag(takes_context=True)
def transform_query(
    context: dict,
    prefix: str = "",
    prefix_sep: str = "_",
    safe: Optional[str] = None,
    **query_transform,
) -> str:
    request: HttpRequest = context["request"]
    querydict = request.GET.copy()
    for key, value in query_transform.items():
        key_ = prefix_sep.join([prefix, key]) if prefix else key
        querydict[key_] = value

    return querydict.urlencode(safe=safe)
