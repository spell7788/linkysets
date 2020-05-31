from django.urls import path

from . import views

app_name = "replies"

urlpatterns = [
    path("post/", views.PostReplyView.as_view(), name="post"),
]
