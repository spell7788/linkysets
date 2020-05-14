from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from .. import views
from ..models import Entry
from .bakery_recipes import entry_recipe
from .common import successful_clean_url_patch

fake = Faker()


class EntryListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entries = entry_recipe.make(_quantity=3)
        cls.entry, *_ = cls.entries

    def test_correctly_resolves_view(self):
        response = self.client.get("/")
        self.assertEqual(
            response.resolver_match.func.__name__, views.EntryListView.as_view().__name__
        )

    def test_returns_correct_status_code(self):
        response = self.client.get(reverse("entries:list"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("entries:list"))
        self.assertTemplateUsed(response, "entries/entry_list.html")

    def test_response_contains_entry_string(self):
        response = self.client.get(reverse("entries:list"))
        self.assertContains(response, str(self.entry))


class AddEntryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()

    def setUp(self):
        self.entry_url = fake.url()
        self.form_data = {"url": self.entry_url}

    def test_correctly_resolves_view(self):
        response = self.client.get(reverse("entries:add"))
        self.assertEqual(
            response.resolver_match.func.__name__, views.AddEntryView.as_view().__name__
        )

    def test_returns_correct_status_code(self):
        response = self.client.get(reverse("entries:add"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("entries:add"))
        self.assertTemplateUsed(response, "entries/add_entry.html")

    @successful_clean_url_patch
    def test_adds_new_anonymous_entry(self, clean_url_mock):
        self.client.post(reverse("entries:add"), self.form_data)
        try:
            entry = Entry.objects.get(url=self.entry_url)
        except Entry.DoesNotExist:
            self.fail(f"Entry wasn't added using data: {self.form_data}")

        self.assertIsNone(entry._author)

    @successful_clean_url_patch
    def test_adds_new_authored_entry(self, clean_url_mock):
        self.client.force_login(self.user)
        self.client.post(reverse("entries:add"), self.form_data)
        try:
            entry = Entry.objects.get(url=self.entry_url)
        except Entry.DoesNotExist:
            self.fail(
                f'Entry wasn\'t added by user "{self.user}" using data: {self.form_data}'
            )

        self.assertEqual(entry._author, self.user)

    @successful_clean_url_patch
    def test_redirects_to_home_on_success(self, clean_url_mock):
        response = self.client.post(reverse("entries:add"), self.form_data)
        self.assertRedirects(response, reverse("entries:list"))


class EntryDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entry = entry_recipe.make()

    def test_correctly_resolves_view(self):
        response = self.client.get(reverse("entries:detail", args=(self.entry.pk,)))
        self.assertEqual(
            response.resolver_match.func.__name__, views.EntryDetailView.as_view().__name__
        )

    def test_returns_correct_status_code(self):
        response = self.client.get(reverse("entries:detail", args=(self.entry.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("entries:detail", args=(self.entry.pk,)))
        self.assertTemplateUsed(response, "entries/entry_detail.html")
