from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from polemicflow.common.models import AuthoredModel, TimestampedModel


class Reply(TimestampedModel, AuthoredModel, MPTTModel):  # type: ignore
    entryset = models.ForeignKey(
        "entries.EntrySet",
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name=_("entry set"),
        help_text=_("Entries set to which the reply belongs."),
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("parent reply"),
        help_text=_("Parent reply if it's not root reply."),
    )
    text = models.CharField(_("text"), max_length=200, help_text=_("Reply text."))

    class Meta:
        verbose_name = _("reply")
        verbose_name_plural = _("replies")

    class MPTTMeta:
        order_insertion_by = ["created"]

    def __str__(self) -> str:
        return self.text
