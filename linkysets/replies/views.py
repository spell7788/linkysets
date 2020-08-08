from typing import Any, Dict, Optional, cast

from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView

from linkysets.common.views import QsObjectMeta, QuerystringObjectsMixin
from linkysets.entries.mixins import PageTitleMixin
from linkysets.entries.models import EntrySet

from .forms import ReplyForm
from .models import Reply


class PostReplyView(PageTitleMixin, QuerystringObjectsMixin, CreateView):
    model = Reply
    form_class = ReplyForm
    template_name = "replies/post_reply.html"
    page_title = _("Post reply")

    qs_objects_meta = [
        QsObjectMeta("entryset", EntrySet),
        QsObjectMeta("reply", Reply, is_required=False),
    ]

    def get_context_data(self, **kwargs) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        return {
            **context,
            "entryset": self.entryset,
            "parent_reply": self.parent_reply,
        }

    def get_form_kwargs(self) -> Dict[Any, Any]:
        kwargs = super().get_form_kwargs()
        user = self.request.user if self.request.user.is_authenticated else None
        return {
            **kwargs,
            "user": user,
            "entryset": self.entryset,
        }

    def get_initial(self) -> Dict[Any, Any]:
        initial_data = super().get_initial()
        return {
            **initial_data,
            "parent": self.parent_reply,
        }

    def get_success_url(self) -> str:
        return self.entryset.get_absolute_url()

    @property
    def entryset(self) -> EntrySet:
        entryset = self.qs_objects["entryset"]
        return cast(EntrySet, entryset[0])

    @property
    def parent_reply(self) -> Optional[Reply]:
        reply = self.qs_objects.get("reply")
        if reply is None:
            return reply
        return cast(Reply, reply[0])
