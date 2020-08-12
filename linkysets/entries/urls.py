from django.urls import path

from . import views

app_name = "entries"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("detail/<str:pk>/", views.EntrySetDetailView.as_view(), name="detail"),
    path("create/", views.create_entryset_view, name="create"),
    path("edit/<str:pk>/", views.edit_entryset_view, name="edit"),
    path("delete/<str:pk>/", views.EntrySetDeleteView.as_view(), name="delete"),
    path("repost/<str:pk>/", views.repost_entry_view, name="repost"),
]
