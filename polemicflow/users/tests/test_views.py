from unittest.mock import PropertyMock, patch

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker

from polemicflow.entries.tests.bakery_recipes import entryset_recipe
from polemicflow.replies.tests.bakery_recipes import reply_recipe

from .. import views
from .bakery_recipes import user_recipe

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
        response = self.client.get(reverse("register"))
        self.assertEqual(
            response.resolver_match.func.__name__, views.RegisterView.as_view().__name__
        )

    def test_get_returns_correnct_status_code(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("register"))
        self.assertTemplateUsed(response, "registration/register.html")

    def test_registers_user_with_correct_data(self):
        self.client.post(reverse("register"), self.data)
        User = get_user_model()
        try:
            User.objects.get(username=self.username)
        except User.DoesNotExist:
            self.fail("User hasn't been created.")

    def test_raises_error_with_incorrect_data(self):
        incorrect_password = fake.password(length=4)
        self.client.post(
            reverse("register"),
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
        response = self.client.post(reverse("register"), self.data, follow=True)
        self.assertRedirects(response, reverse("entries:home"))


class UserDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()
        entryset_list = entryset_recipe.make(author=cls.user, _quantity=3)
        cls.entryset_list = sorted(entryset_list, key=lambda es: es.created, reverse=True)
        reply_list = reply_recipe.make(author=cls.user, _quantity=3)
        cls.reply_list = sorted(reply_list, key=lambda r: r.created, reverse=True)

    def test_correctly_resolves_view(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"username": self.user.username})
        )
        self.assertEqual(
            response.resolver_match.func.__name__, views.UserDetailView.as_view().__name__
        )

    def test_get_returns_ok_status_code(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"username": self.user.username})
        )
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"username": self.user.username})
        )
        self.assertTemplateUsed(response, "users/user_detail.html")

    def test_context_has_entrysets_page(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"username": self.user.username})
        )
        page = response.context.get("entrysets_page")
        self.assertIsNotNone(page)
        self.assertEqual(page.number, 1)

    def test_context_has_replies_page(self):
        response = self.client.get(
            reverse("users:detail", kwargs={"username": self.user.username})
        )
        page = response.context.get("replies_page")
        self.assertIsNotNone(page)
        self.assertEqual(page.number, 1)

    @patch(
        "polemicflow.users.views.UserDetailView.entrysets_per_page",
        new_callable=PropertyMock,
        return_value=1,
    )
    def test_gets_right_entrysets_page(self, property_mock):
        page_number = fake.random_int(min=1, max=len(self.entryset_list) - 1)
        response = self.client.get(
            reverse("users:detail", kwargs={"username": self.user.username}),
            {"sets_page": page_number},
        )
        page = response.context["entrysets_page"]
        self.assertEqual(page.number, page_number)
        entryset_pk = self.entryset_list[page_number - 1].pk
        self.assertIn(entryset_pk, [entryset.pk for entryset in page])

    @patch(
        "polemicflow.users.views.UserDetailView.replies_per_page",
        new_callable=PropertyMock,
        return_value=1,
    )
    def test_gets_right_replies_page(self, property_mock):
        page_number = fake.random_int(min=1, max=len(self.reply_list) - 1)
        response = self.client.get(
            reverse("users:detail", kwargs={"username": self.user.username}),
            {"replies_page": page_number},
        )
        page = response.context["replies_page"]
        self.assertEqual(page.number, page_number)
        reply_pk = self.reply_list[page_number - 1].pk
        self.assertIn(reply_pk, [reply.pk for reply in page])
