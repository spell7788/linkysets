from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DetailView

from linkysets.entries.mixins import PageTitleMixin

from .forms import AuthenticationForm, UserCreationForm
from .models import User


class LoginView(PageTitleMixin, DjangoLoginView):
    authentication_form = AuthenticationForm
    page_title = _("Login")

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hero_title"] = self.page_title
        return context


class RegisterView(PageTitleMixin, CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("entries:home")
    page_title = _("Register")

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hero_title"] = self.page_title
        return context


class UserDetailView(PageTitleMixin, DetailView):
    template_name = "users/user_detail.html"
    queryset = User.objects.num_entrysets().num_replies()
    slug_field = "username"
    slug_url_kwarg = "username"
    title_object_name = "object"

    entrysets_per_page: int = 5
    replies_per_page: int = 5

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        entrysets_page_num = self.request.GET.get("sets_page", 1)
        entrysets_qs = self.object.entryset_set.order_by("-created")  # type: ignore
        context["entrysets_page"] = Paginator(entrysets_qs, self.entrysets_per_page,).page(
            entrysets_page_num
        )

        replies_page_num = self.request.GET.get("replies_page", 1)
        replies_qs = self.object.reply_set.select_related(  # type: ignore
            "parent", "entryset"
        ).order_by("-created")
        context["replies_page"] = Paginator(replies_qs, self.replies_per_page,).page(
            replies_page_num
        )

        return context
