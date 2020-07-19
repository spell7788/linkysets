from typing import Optional

from django import template
from django.http import HttpRequest

register = template.Library()


@register.simple_tag(takes_context=True)
def transform_query(context: dict, safe: Optional[str] = None, **kwargs) -> str:
    request: HttpRequest = context["request"]
    querydict = request.GET.copy()
    for key, value in kwargs.items():
        querydict[key] = value

    return querydict.urlencode(safe=safe)
