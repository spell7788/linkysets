from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import reverse  # type: ignore
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from polemicflow.common.models import AuthoredModel, TimestampedModel

if TYPE_CHECKING:
    EntrySetManagerBase = models.Manager["EntrySet"]
else:
    EntrySetManagerBase = models.Manager


class EntrySetManager(EntrySetManagerBase):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related("entries")
        return qs


class EntrySet(TimestampedModel, AuthoredModel):
    name = models.CharField(
        _("name"), max_length=50, blank=True, help_text=_("Entry set name (optional).")
    )
    entries = models.ManyToManyField(
        "Entry",
        related_name="sets",
        verbose_name=_("entries"),
        help_text=_("Entries that this set contains."),
    )

    objects = EntrySetManager()

    class Meta:
        verbose_name = _("entry set")
        verbose_name_plural = _("entry sets")

    def __str__(self) -> str:
        if self.name:
            return self.name

        username = self.get_author().username
        return _("%(username)s's set") % {"username": username or _("Anonymous")}

    def clean(self):
        if self.pk is not None and self.entries.count() < 1:
            raise ValidationError(
                "At least one added entry is required.", code="entry_required"
            )

    def get_absolute_url(self) -> str:
        return reverse("entries:detail", kwargs={"pk": self.pk})


class Entry(models.Model):
    class EntryType(models.IntegerChoices):
        URL = 0, _("URL")
        IMAGE = 1, _("Image")
        VIDEO = 2, _("Video")
        YT_VIDEO = 3, _("Youtube video")

    type = models.PositiveSmallIntegerField(
        _("type"),
        choices=EntryType.choices,
        blank=True,
        default=EntryType.URL,
        help_text=_("Supported entry type."),
    )
    url = models.URLField(
        _("URL"), max_length=400, help_text=_("URL of the resource to share.")
    )
    label = models.CharField(
        _("label"), max_length=100, blank=True, help_text=_("Entry label (optional).")
    )
    origin = models.ForeignKey(
        EntrySet,
        on_delete=models.SET_NULL,
        related_name="original_entries",
        null=True,
        editable=False,
        verbose_name=_("origin"),
        help_text=_("Original entry set of the entry."),
    )

    class Meta:
        verbose_name = _("entry")
        verbose_name_plural = _("entries")

    def __str__(self):
        return self.url


class Reply(TimestampedModel, AuthoredModel, MPTTModel):
    set = models.ForeignKey(
        EntrySet,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name=_("entry set"),
        help_text=_("Reply's entry set."),
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
