from django.db import models
from django.utils.translation import ugettext_lazy as _


class Entry(models.Model):
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
