from typing import Union

from django import template
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from ..models import AuthoredModel
from ..typing import SupportsStr

register = template.Library()


@register.simple_tag
def get_username(instance: AuthoredModel) -> Union[str, SupportsStr]:
    author = instance.get_author()
    if isinstance(author, AnonymousUser):
        return settings.ANONYMOUS_USERNAME

    return author.username
