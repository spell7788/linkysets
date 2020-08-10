from linkysets.common.backends import ObjectPermissionBackend

from .models import EntrySet


class EntrySetPermissionBackend(ObjectPermissionBackend):
    model = EntrySet
    user_rel_field = "author"
