from typing import ClassVar, Optional

from linkysets.common.mixins import ObjectPermissionMixin
from linkysets.common.typing import SupportsStr

from .utils import join_page_title


class PageTitleMixin:
    page_title: ClassVar[Optional[SupportsStr]] = None
    title_object_name: ClassVar[Optional[str]] = None
    join_extension: ClassVar[bool] = True

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_full_title()
        return context

    def get_full_title(self) -> SupportsStr:
        title = self.get_title()
        if self.join_extension:
            return join_page_title(title)
        return title

    def get_title(self) -> str:
        if self.page_title is None and self.title_object_name is None:
            raise RuntimeError(
                'Provide "page_title" or "title_object_name"'
                'or override "get_title" method completely.'
            )
        if self.page_title:
            return self.page_title

        return str(getattr(self, self.title_object_name))


class EntrySetPermissionMixin(ObjectPermissionMixin):
    pass
