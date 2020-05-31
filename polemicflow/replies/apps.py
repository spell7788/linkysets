from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RepliesConfig(AppConfig):
    name = "polemicflow.replies"
    verbose_name = _("replies")
