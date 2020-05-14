from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import EntryForm
from .models import Entry


class EntryListView(ListView):
    model = Entry
    template_name = "entries/entry_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entry_form"] = EntryForm()
        return context


class AddEntryView(CreateView):
    form_class = EntryForm
    template_name = "entries/add_entry.html"
    success_url = reverse_lazy("entries:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        # AnonymousUser's pk is None
        if user.pk is not None:
            kwargs["user"] = user

        return kwargs
