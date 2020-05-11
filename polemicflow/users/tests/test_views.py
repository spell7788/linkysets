from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker

from .. import views

fake = Faker()


class RegisterViewTests(TestCase):
    def setUp(self):
        self.username = fake.user_name()
        self.password = fake.password()
        self.data = {
            "username": self.username,
            "password1": self.password,
            "password2": self.password,
        }

    def test_correctly_resolves_view(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(
            response.resolver_match.func.__name__, views.RegisterView.as_view().__name__
        )

    def test_get_returns_correnct_status_code(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("users:register"))
        self.assertTemplateUsed(response, "registration/register.html")

    def test_registers_user_with_correct_data(self):
        self.client.post(reverse("users:register"), self.data)
        User = get_user_model()
        try:
            User.objects.get(username=self.username)
        except User.DoesNotExist:
            self.fail("User hasn't been created.")

    def test_raises_error_with_incorrect_data(self):
        incorrect_password = fake.password(length=4)
        self.client.post(
            reverse("users:register"),
            {
                "username": self.username,
                "password1": incorrect_password,
                "password2": incorrect_password,
            },
        )
        User = get_user_model()
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.username)

    def test_redirects_to_home_page_after_registration(self):
        response = self.client.post(reverse("users:register"), self.data, follow=True)
        self.assertRedirects(response, reverse("entries:list"))
