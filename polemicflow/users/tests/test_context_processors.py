from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase

from .bakery_recipes import user_recipe


class LoginFormContextProcessorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()

    def test_adds_login_form_when_no_user(self):
        response = self.client.get("/")
        login_form = response.context.get("login_form")
        self.assertIsInstance(login_form, AuthenticationForm)

    def test_no_login_form_in_context_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        with self.assertRaises(KeyError):
            response.context["login_form"]
