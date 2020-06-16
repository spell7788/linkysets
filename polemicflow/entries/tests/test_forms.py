from unittest.mock import patch

import requests
from django.test import TestCase
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from ..forms import EntryForm, EntryFormset
from ..models import Entry
from .bakery_recipes import entry_recipe, entryset_recipe
from .common import EntryFormsetDataMixin, head_response_factory

fake = Faker()


class EntryFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()
        cls.entry = entry_recipe.make()

    def setUp(self):
        self.label = fake.pystr()
        self.valid_data = {"url": self.entry.url, "label": self.label}
        self.head_response = head_response_factory(
            get_content_type=lambda response: fake.mime_type()
        )

    @patch("requests.Session.head")
    def test_form_is_valid_when_url_passed(self, head_mock):
        head_mock.side_effect = self.head_response
        form = EntryForm(self.valid_data)
        self.assertTrue(form.is_valid())

    @patch("requests.Session.head")
    def test_form_fail_when_invalid_url(self, head_mock):
        head_mock.side_effect = self.head_response
        invalid_data = {**self.valid_data, "url": fake.pystr()}
        form = EntryForm(invalid_data)
        self.assertFalse(form.is_valid())

    @patch("requests.Session.head")
    def test_clean_raises_validation_error(self, head_mock):
        head_mock.side_effect = requests.RequestException()
        form = EntryForm(self.valid_data)
        self.assertFalse(form.is_valid())
        try:
            validation_error = form.errors["url"][0]
        except KeyError:
            self.fail(f"Validation error was not added: {form.errors.as_data()}")

        self.assertEqual(
            str(validation_error), f"Could not reach target url: {self.entry.url}"
        )

    @patch("requests.Session.head")
    def test_successfully_saves_entry_instance(self, head_mock):
        head_mock.side_effect = self.head_response
        form = EntryForm(self.valid_data)
        entry = form.save()
        self.assertIsNotNone(entry.pk)
        # getting entry from db shouldn't raise errors
        entry = Entry.objects.get(pk=entry.pk)

    @patch("requests.Session.head")
    def test_skips_url_request_on_resave_with_same_url(self, head_mock):
        form = EntryForm(self.valid_data, instance=self.entry)
        form.save()
        head_mock.assert_not_called()

    @patch("requests.Session.head")
    def test_requests_url_on_resave_if_url_changed(self, head_mock):
        head_mock.side_effect = self.head_response
        form = EntryForm(self.valid_data)
        form.save()
        head_mock.assert_called_once()


class EntryFormsetTests(EntryFormsetDataMixin, TestCase):
    def setUp(self):
        self.entryset = entryset_recipe.make()
        self.valid_data = self.get_data_from_entryset(self.entryset)
        self.head_response = head_response_factory()

    def test_gets_correct_prefix(self):
        prefix = EntryFormset.get_default_prefix()
        self.assertEqual(prefix, "entries")

    def test_gets_correct_queryset_if_formset_instance(self):
        formset = EntryFormset(self.valid_data, instance=self.entryset)
        qs = formset.get_queryset()
        entries_reprs = (repr(entry) for entry in self.entryset.entries.all())
        self.assertQuerysetEqual(qs, entries_reprs)

    def test_gets_empty_queryset_if_no_formset_instance(self):
        formset = EntryFormset(self.valid_data)
        qs = formset.get_queryset()
        self.assertEqual(len(qs), 0)

    @patch("requests.Session.head")
    def test_assigns_origin_to_entries_on_save(self, head_mock):
        head_mock.side_effect = self.head_response
        formset = EntryFormset(self.valid_data, instance=self.entryset)
        self.assertTrue(formset.is_valid())
        entries = formset.save()
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertEqual(entry.origin, self.entryset)

    @patch("requests.Session.head")
    def test_clean_validation_error_for_same_urls(self, head_mock):
        head_mock.side_effect = self.head_response
        invalid_data = {
            **self.valid_data,
            "entries-1-url": self.valid_data["entries-0-url"],
        }
        formset = EntryFormset(invalid_data, instance=self.entryset)
        self.assertFalse(formset.is_valid())
        validation_error = formset.non_form_errors()[0]
        self.assertEqual(str(validation_error), "Entries urls must be unique in one set.")

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
        formset = EntryFormset(valid_data, instance=self.entryset)
        self.assertTrue(formset.is_valid())
        entries = formset.save()
        self.assertEqual(len(entries), 3)
        *_, entry = entries
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
        formset = EntryFormset(valid_data, instance=self.entryset)
        self.assertTrue(formset.is_valid())
        entries = formset.save()
        entry, *_ = entries
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.label, label)

    @patch("requests.Session.head")
    def test_deletes_entry(self, head_mock):
        head_mock.side_effect = self.head_response
        delete_id = self.valid_data["entries-1-id"]
        valid_data = {
            **self.valid_data,
            "entries-1-DELETE": "on",
        }
        formset = EntryFormset(valid_data, instance=self.entryset)
        self.assertTrue(formset.is_valid())
        entries = formset.save()
        self.assertEqual(len(entries), 1)
        delete_obj = formset.deleted_objects[0]
        self.assertEqual(delete_obj.pk, delete_id)
