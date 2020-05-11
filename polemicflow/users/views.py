from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserCreationForm


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("entries:list")
