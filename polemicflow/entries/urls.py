from django.urls import path

from .views import EntryListView

app_name = "entries"

urlpatterns = [
    path("", EntryListView.as_view(), name="list")
]
