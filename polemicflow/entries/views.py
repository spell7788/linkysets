from django.http import HttpRequest, HttpResponse
from django.shortcuts import Http404, redirect, render  # type: ignore
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import EntryForm, ReplyForm
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


def entry_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        entry = Entry.objects.filter(pk=pk).prefetch_related("replies").get()
    except Entry.DoesNotExist:
        params = {"pk": pk}
        raise Http404(f"Entry doesn't exist. Passed parameters: {params}")

    user = request.user if request.user.is_authenticated else None
    form = ReplyForm(entry=entry, user=user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(entry)

    context = {"entry": entry, "reply_form": form}
    return render(request, "entries/entry_detail.html", context)
