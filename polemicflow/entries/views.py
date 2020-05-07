from django.views.generic import ListView

from .models import Entry


class EntryListView(ListView):
    model = Entry
    template_name = "entries/entry_list.html"
