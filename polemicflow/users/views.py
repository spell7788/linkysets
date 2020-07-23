from __future__ import annotations

from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DetailView

from .forms import AuthenticationForm, UserCreationForm
from .models import User


class LoginView(DjangoLoginView):
    authentication_form = AuthenticationForm

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["hero_title"] = _("Login")
        return context


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("entries:home")

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["hero_title"] = _("Register")
        return context


class UserDetailView(DetailView):
    template_name = "users/user_detail.html"
    queryset = User.objects.num_entrysets().num_replies()
    slug_field = "username"
    slug_url_kwarg = "username"

    entrysets_per_page: int = 5
    replies_per_page: int = 5

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        entrysets_page_num = self.request.GET.get("sets_page", 1)
        context["entrysets_page"] = Paginator(
            self.object.entryset_set.num_entries().num_replies().order_by("-created"),
            self.entrysets_per_page,
        ).page(entrysets_page_num)

        replies_page_num = self.request.GET.get("replies_page", 1)
        context["replies_page"] = Paginator(
            self.object.reply_set.select_related("parent", "entryset").order_by("-created"),
            self.replies_per_page,
        ).page(replies_page_num)

        return context
