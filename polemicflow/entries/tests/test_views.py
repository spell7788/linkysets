from unittest.mock import patch

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import translation
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from .. import views
from ..models import EntrySet
from .bakery_recipes import entryset_recipe
from .common import get_mock_response

fake = Faker()


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entryset_list = entryset_recipe.make(_quantity=2, _fill_optional=True)
        cls.entryset, *_ = cls.entryset_list

    def test_correctly_resolves_view(self):
        response = self.client.get("/")
        self.assertEqual(
            response.resolver_match.func.__name__, views.HomeView.as_view().__name__
        )

    def test_returns_correct_status_code(self):
        response = self.client.get(reverse("entries:home"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("entries:home"))
        self.assertTemplateUsed(response, "entries/home.html")

    def test_response_contains_entry_string(self):
        response = self.client.get(reverse("entries:home"))
        self.assertContains(response, str(self.entryset))


class CreateEntrySetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()

    def setUp(self):
        self.client.force_login(self.user)
        self.entryset_name = fake.pystr()
        self.form0_url = fake.url()
        self.form0_label = fake.pystr()
        self.form0_mime_type = fake.mime_type()
        self.valid_data = {
            "name": self.entryset_name,
            # management form data
            "original_entries-TOTAL_FORMS": "1",
            "original_entries-INITIAL_FORMS": "0",
            # ---
            "original_entries-0-url": self.form0_url,
            "original_entries-0-label": self.form0_label,
        }
        self.valid_head_response = get_mock_response(self.form0_url, self.form0_mime_type)

    def test_correctly_resolves_view(self):
        response = self.client.get(reverse("entries:create"))
        self.assertEqual(
            response.resolver_match.func.__name__, views.create_entryset_view.__name__
        )

    def test_returns_correct_status_code(self):
        response = self.client.get(reverse("entries:create"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("entries:create"))
        self.assertTemplateUsed(response, "entries/entryset_form.html")

    @patch("requests.Session.head")
    def test_successfully_creates_entryset(self, head_mock):
        head_mock.return_value = self.valid_head_response
        self.client.post(reverse("entries:create"), self.valid_data)
        EntrySet.objects.get(name=self.entryset_name)

    @patch("requests.Session.head")
    def test_redirects_after_entryset_created(self, head_mock):
        head_mock.return_value = self.valid_head_response
        response = self.client.post(reverse("entries:create"), self.valid_data)
        self.assertRedirects(response, reverse("entries:home"))

    @patch("requests.Session.head")
    def test_creates_entryset_without_optional_name(self, head_mock):
        head_mock.return_value = self.valid_head_response
        self.valid_data["name"] = ""
        self.client.post(reverse("entries:create"), self.valid_data)
        entryset = EntrySet.objects.latest("created")
        self.assertEqual(entryset.name, "")

    def test_contains_field_is_required_error(self):
        invalid_data = {**self.valid_data, "original_entries-0-url": ""}
        with translation.override(None, deactivate=True):
            response = self.client.post(reverse("entries:create"), invalid_data)
        self.assertContains(response, "This field is required.")

    def test_entryset_is_not_created_without_valid_entries(self):
        invalid_data = {**self.valid_data, "original_entries-0-url": ""}
        self.client.post(reverse("entries:create"), invalid_data)
        with self.assertRaises(EntrySet.DoesNotExist):
            EntrySet.objects.get(name=self.entryset_name)

    @patch("requests.Session.head")
    def test_creates_entryset_for_anonymous_user(self, head_mock):
        head_mock.return_value = self.valid_head_response
        self.client.logout()
        self.client.post(reverse("entries:create"), self.valid_data)
        EntrySet.objects.get(name=self.entryset_name)


class EntrySetDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entryset = entryset_recipe.make(_fill_optional=True)

    def test_correctly_resolves_view(self):
        response = self.client.get(
            reverse("entries:detail", kwargs={"pk": self.entryset.pk})
        )
        self.assertEqual(
            response.resolver_match.func.__name__, views.EntrySetDetailView.__name__
        )

    def test_returns_correct_status_code(self):
        response = self.client.get(
            reverse("entries:detail", kwargs={"pk": self.entryset.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(
            reverse("entries:detail", kwargs={"pk": self.entryset.pk})
        )
        self.assertTemplateUsed(response, "entries/entryset_detail.html")

    def test_contains_entryset_string(self):
        response = self.client.get(
            reverse("entries:detail", kwargs={"pk": self.entryset.pk})
        )
        self.assertContains(response, str(self.entryset))

    def test_contains_related_rendered_entries(self):
        response = self.client.get(
            reverse("entries:detail", kwargs={"pk": self.entryset.pk})
        )
        entries = self.entryset.entries.all()
        self.assertGreater(len(entries), 0)
        with translation.override(None, deactivate=True):
            for entry in entries:
                with self.subTest(entry=entry):
                    self.assertContains(response, entry.render())
