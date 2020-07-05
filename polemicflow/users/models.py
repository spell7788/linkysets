from django.conf import settings
from django.contrib.auth.models import AbstractUser

from polemicflow.common.utils import Proxy


class User(AbstractUser):
    pass


class AnonymousUserProxy(Proxy):
    @property
    def username(self) -> str:
        return settings.ANONYMOUS_USERNAME
