"""linkysets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib.auth import views as django_auth_views
from django.urls import include, path
from linkysets.users import views as auth_views

auth_urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login",),
    path("logout/", django_auth_views.LogoutView.as_view(), name="logout"),
    path("register/", auth_views.RegisterView.as_view(), name="register"),
]

urlpatterns = auth_urlpatterns + [
    path("", include("linkysets.entries.urls", namespace="entries")),
    path("replies/", include("linkysets.replies.urls", namespace="replies")),
    path("users/", include("linkysets.users.urls", namespace="users")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls))  # noqa: DJ05
    ]
