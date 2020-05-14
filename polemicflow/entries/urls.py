from django.urls import path

from . import views

app_name = "entries"

urlpatterns = [
    path("", views.EntryListView.as_view(), name="list"),
    path("add/", views.AddEntryView.as_view(), name="add"),
]
