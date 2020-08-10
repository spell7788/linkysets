from typing import Any, ClassVar, Dict, Sequence

from django.db.models import Model
from django.http import HttpRequest


class ObjectPermissionMixin:
    request: HttpRequest
    object: Model

    perms: ClassVar[Sequence[str]] = ["view", "add", "change", "delete"]

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore
        user = self.request.user
        model = type(self.object)
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        object_perms = {}
        for perm in self.perms:
            perm_codename = f"{app_label}.{perm}_{model_name}"
            object_perms[f"has_{perm}_perm"] = user.has_perm(perm_codename, self.object)

        context["object_perms"] = object_perms
        return context
