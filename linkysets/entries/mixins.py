from typing import Any, ClassVar, Dict, Optional, cast

from linkysets.common.mixins import ObjectPermissionMixin
from linkysets.common.typing import SupportsStr

from .utils import join_page_title


class PageTitleMixin:
    page_title: ClassVar[Optional[SupportsStr]] = None
    title_object_name: ClassVar[Optional[str]] = None
    join_extension: ClassVar[bool] = True

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore
        context["page_title"] = self.get_full_title()
        return context

    def get_full_title(self) -> SupportsStr:
        title = self.get_title()
        if self.join_extension:
            return join_page_title(title)
        return title

    def get_title(self) -> SupportsStr:
        if self.page_title is None and self.title_object_name is None:
            raise RuntimeError(
                'Provide "page_title" or "title_object_name"'
                'or override "get_title" method completely.'
            )
        if self.page_title:
            return self.page_title

        title_object_name = cast(str, self.title_object_name)
        return getattr(self, title_object_name)


class EntrySetPermissionMixin(ObjectPermissionMixin):
    pass
