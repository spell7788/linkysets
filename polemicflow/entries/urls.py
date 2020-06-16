from django.urls import path

from . import views

app_name = "entries"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("detail/<str:pk>/", views.EntrySetDetailView.as_view(), name="detail"),
    path("create/", views.create_entryset_view, name="create"),
    path("update/<str:pk>/", views.update_entryset_view, name="update"),
    path("repost/<str:pk>/", views.repost_entry_view, name="repost"),
]
