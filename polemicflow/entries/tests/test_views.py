from unittest.mock import patch

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import translation
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from .. import views
from ..models import Entry, EntrySet
from .bakery_recipes import entry_recipe, entryset_recipe
from .common import EntryFormsetDataMixin, head_response_factory

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


class CreateEntrySetTests(EntryFormsetDataMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()

    def setUp(self):
        self.client.force_login(self.user)
        self.entryset_name = fake.pystr()
        self.valid_data = {
            **self.get_random_data(),
            "entries-INITIAL_FORMS": "0",
            "name": self.entryset_name,
        }
        self.head_response = head_response_factory(
            get_content_type=lambda response: fake.mime_type()
        )

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
        head_mock.side_effect = self.head_response
        self.client.post(reverse("entries:create"), self.valid_data)
        EntrySet.objects.get(name=self.entryset_name)

    @patch("requests.Session.head")
    def test_redirects_after_entryset_created(self, head_mock):
        head_mock.side_effect = self.head_response
        response = self.client.post(reverse("entries:create"), self.valid_data)
        self.assertRedirects(response, reverse("entries:home"))

    @patch("requests.Session.head")
    def test_creates_entryset_without_optional_name(self, head_mock):
        head_mock.side_effect = self.head_response
        self.valid_data["name"] = ""
        self.client.post(reverse("entries:create"), self.valid_data)
        entryset = EntrySet.objects.latest("created")
        self.assertEqual(entryset.name, "")

    def test_contains_field_is_required_error(self):
        invalid_data = {**self.valid_data, "entries-0-url": ""}
        with translation.override(None, deactivate=True):
            response = self.client.post(reverse("entries:create"), invalid_data)
        self.assertContains(response, "This field is required.")

    def test_entryset_is_not_created_without_valid_entries(self):
        invalid_data = {**self.valid_data, "entries-0-url": ""}
        self.client.post(reverse("entries:create"), invalid_data)
        with self.assertRaises(EntrySet.DoesNotExist):
            EntrySet.objects.get(name=self.entryset_name)

    @patch("requests.Session.head")
    def test_creates_entryset_for_anonymous_user(self, head_mock):
        head_mock.side_effect = self.head_response
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

    def test_contains_rendered_entries(self):
        response = self.client.get(
            reverse("entries:detail", kwargs={"pk": self.entryset.pk})
        )
        with translation.override(None, deactivate=True):
            for entry in self.entryset.entries.all():
                with self.subTest(entry=entry):
                    if entry.type != Entry.EntryType.URL:
                        text = entry.render()
                    else:
                        text = entry.url

                    self.assertContains(response, text)


class EditEntrySetTests(EntryFormsetDataMixin, TestCase):
    def setUp(self):
        self.entryset = entryset_recipe.make()
        self.valid_data = self.get_data_from_entryset(self.entryset)
        self.head_response = head_response_factory(
            get_content_type=lambda response: fake.mime_type()
        )

    def test_correctly_resolves_view(self):
        response = self.client.get(reverse("entries:edit", kwargs={"pk": self.entryset.pk}))
        self.assertEqual(
            response.resolver_match.func.__name__, views.edit_entryset_view.__name__
        )

    def test_get_returns_ok_status_code(self):
        response = self.client.get(reverse("entries:edit", kwargs={"pk": self.entryset.pk}))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("entries:edit", kwargs={"pk": self.entryset.pk}))
        self.assertTemplateUsed(response, "entries/entryset_form.html")

    @patch("requests.Session.head")
    def test_post_redirects_on_success(self, head_mock):
        head_mock.side_effect = self.head_response
        response = self.client.post(
            reverse("entries:edit", kwargs={"pk": self.entryset.pk}), self.valid_data
        )
        self.assertRedirects(response, reverse("entries:home"))

    @patch("requests.Session.head")
    def test_adds_entry(self, head_mock):
        head_mock.side_effect = self.head_response
        url, label = fake.url(), fake.pystr()
        valid_data = {
            **self.valid_data,
            "entries-TOTAL_FORMS": "3",
            "entries-2-url": url,
            "entries-2-label": label,
        }
        self.client.post(
            reverse("entries:edit", kwargs={"pk": self.entryset.pk}), valid_data
        )
        entry = self.entryset.entries.get(url=url)
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.label, label)

    @patch("requests.Session.head")
    def test_updates_entry(self, head_mock):
        head_mock.side_effect = self.head_response
        url, label = fake.url(), fake.pystr()
        valid_data = {
            **self.valid_data,
            "entries-0-url": url,
            "entries-0-label": label,
        }
        self.client.post(
            reverse("entries:edit", kwargs={"pk": self.entryset.pk}), valid_data
        )
        entry = self.entryset.entries.get(url=url)
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.label, label)

    @patch("requests.Session.head")
    def test_deletes_entry(self, head_mock):
        head_mock.side_effect = self.head_response
        delete_id = self.valid_data["entries-0-id"]
        valid_data = {
            **self.valid_data,
            "entries-0-DELETE": "on",
        }
        self.client.post(
            reverse("entries:edit", kwargs={"pk": self.entryset.pk}), valid_data
        )
        self.assertFalse(Entry.objects.filter(pk=delete_id).exists())


class RepostEntryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entry = entry_recipe.make()

    def test_correctly_resolves_view(self):
        response = self.client.get(reverse("entries:repost", kwargs={"pk": self.entry.pk}))
        self.assertEqual(
            response.resolver_match.func.__name__, views.repost_entry_view.__name__
        )

    def test_get_returns_not_allowed_status_code(self):
        response = self.client.get(reverse("entries:repost", kwargs={"pk": self.entry.pk}))
        self.assertEqual(response.status_code, 405)

    def test_post_redirects_to_entryset_update(self):
        response = self.client.post(reverse("entries:repost", kwargs={"pk": self.entry.pk}))
        entryset = EntrySet.objects.latest("id")
        self.assertRedirects(response, reverse("entries:edit", kwargs={"pk": entryset.pk}))

    def test_created_entryset_has_reposted_entry(self):
        self.client.post(reverse("entries:repost", kwargs={"pk": self.entry.pk}))
        entryset = EntrySet.objects.latest("id")
        entryset.entries.get(pk=self.entry.pk)

    def test_returns_not_found_if_nonexistent_entry(self):
        response = self.client.post(reverse("entries:repost", kwargs={"pk": fake.pyint()}))
        self.assertEqual(response.status_code, 404)
