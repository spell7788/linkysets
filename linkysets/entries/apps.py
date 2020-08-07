from django.apps import AppConfig
from django.db.models import CharField
from django.db.models.functions import Lower
from django.utils.translation import ugettext_lazy as _


class EntriesConfig(AppConfig):
    name = "linkysets.entries"
    verbose_name = _("Entries")

    def ready(self) -> None:
        CharField.register_lookup(Lower)
