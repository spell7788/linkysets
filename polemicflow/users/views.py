from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView

from .forms import AuthenticationForm, UserCreationForm


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
