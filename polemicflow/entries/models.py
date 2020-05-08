from typing import Union

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from polemicflow.users.models import User


class AbstractBaseEntry(models.Model):
    _author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="author",
        verbose_name=_("author"),
        help_text=_("The user who posted entry."),
    )
    timestamp = models.DateTimeField(
        _("timestamp"),
        auto_now_add=True,
        editable=False,
        help_text=_("Date and time of entry creation."),
    )

    class Meta:
        abstract = True

    @property
    def author(self) -> Union[User, AnonymousUser]:
        return self._author or AnonymousUser()


class Entry(AbstractBaseEntry):
    url = models.URLField(
        _("URL"),
        max_length=400,
        unique=True,
        help_text=_("URL of the resource you want to share."),
    )
    image_url = models.URLField(
        _("image URL"),
        max_length=400,
        blank=True,
        help_text=_("The image of the resource."),
    )

    def __str__(self) -> str:
        return self.url

    class Meta:
        verbose_name = _("entry")
        verbose_name_plural = _("entries")
