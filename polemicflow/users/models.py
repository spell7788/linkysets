from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.shortcuts import reverse

from polemicflow.common.utils import Proxy

from .managers import UserQuerySet


class User(AbstractUser):
    objects = UserManager.from_queryset(UserQuerySet)()

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class AnonymousUserProxy(Proxy):
    @property
    def username(self) -> str:
        return settings.ANONYMOUS_USERNAME

    def get_absolute_url(self) -> str:
        return "#"
