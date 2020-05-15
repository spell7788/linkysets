from typing import Union

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.shortcuts import reverse  # type: ignore
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

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

    class Meta:
        verbose_name = _("entry")
        verbose_name_plural = _("entries")

    def __str__(self) -> str:
        return self.url

    def get_absolute_url(self):
        return reverse("entries:detail", args=(self.pk,))


class Reply(AbstractBaseEntry, MPTTModel):
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name=_("related entry"),
        help_text=_("Entry to which reply is attached."),
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("parent reply"),
        help_text=_("Parent reply if it's not entry reply."),
    )
    text = models.CharField(_("text"), max_length=200, help_text=_("Reply text."))

    class Meta:
        verbose_name = _("reply")
        verbose_name_plural = _("replies")

    class MPTTMeta:
        order_insertion_by = ["timestamp"]

    def __str__(self) -> str:
        return self.text
