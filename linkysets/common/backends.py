from typing import Any, ClassVar, Optional, Type

from django.db.models import Model


class ObjectPermissionBackend:
    model: ClassVar[Type[Model]]
    user_rel_field: ClassVar[str]

    def has_perm(self, user: Any, perm: str, obj: Optional[Model] = None) -> bool:
        if obj is None or not user.is_active:
            return False

        if perm == f"{self.model._meta.app_label}.view_{self.model._meta.model_name}":
            return True

        obj_user = getattr(obj, self.user_rel_field)
        if obj_user and obj_user.pk == user.pk:
            return True

        return False
