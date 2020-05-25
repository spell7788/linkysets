from django.shortcuts import reverse
from django.test import TestCase
from django.utils import translation
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from .. import views
from ..models import Entry, EntrySet
from .bakery_recipes import entryset_recipe
from .common import passing_clean_url_patch

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
        self.valid_data = {
            "name": self.entryset_name,
            # management form data
            "original_entries-TOTAL_FORMS": "1",
            "original_entries-INITIAL_FORMS": "0",
            # ---
            "original_entries-0-type": fake.random_element(Entry.EntryType.values),
            "original_entries-0-url": fake.url(),
            "original_entries-0-label": fake.pystr(),
        }

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

    @passing_clean_url_patch
    def test_successfully_creates_entryset(self, clean_url_mock):
        self.client.post(reverse("entries:create"), self.valid_data)
        EntrySet.objects.get(name=self.entryset_name)

    @passing_clean_url_patch
    def test_redirects_after_entryset_created(self, clean_url_mock):
        response = self.client.post(reverse("entries:create"), self.valid_data)
        self.assertRedirects(response, reverse("entries:home"))

    @passing_clean_url_patch
    def test_creates_entryset_without_optional_name(self, clean_url_mock):
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

    @passing_clean_url_patch
    def test_creates_entryset_for_anonymous_user(self, clean_url_mock):
        self.client.logout()
        self.client.post(reverse("entries:create"), self.valid_data)
        EntrySet.objects.get(name=self.entryset_name)
