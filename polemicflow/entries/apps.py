from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EntriesConfig(AppConfig):
    name = "polemicflow.entries"
    verbose_name = _("Entries")
