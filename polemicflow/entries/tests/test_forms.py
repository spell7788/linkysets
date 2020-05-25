from unittest.mock import patch

from django.test import TestCase
from faker import Faker
from requests import Response

from polemicflow.users.tests.bakery_recipes import user_recipe

from ..forms import EntryForm
from ..models import Entry
from .bakery_recipes import entry_recipe
from .common import failing_clean_url_patch, passing_clean_url_patch

fake = Faker()


class EntryFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()
        cls.entry = entry_recipe.make()

    def setUp(self):
        self.entry_type = fake.random_element(Entry.EntryType.values)
        self.entry_label = fake.pystr()
        self.valid_data = {
            "type": self.entry_type,
            "url": self.entry.url,
            "label": self.entry_label,
        }

    @passing_clean_url_patch
    def test_form_is_valid_when_url_passed(self, clean_url_mock):
        form = EntryForm(self.valid_data)
        self.assertTrue(form.is_valid())

    @passing_clean_url_patch
    def test_form_fail_when_invalid_url(self, clean_url_mock):
        invalid_data = {**self.valid_data, "url": fake.pystr()}
        form = EntryForm(invalid_data)
        self.assertFalse(form.is_valid())

    @failing_clean_url_patch
    def test_clean_url_raises_validation_error(self, clean_url_mock):
        form = EntryForm(self.valid_data)
        self.assertFalse(form.is_valid())
        try:
            validation_error = form.errors["url"][0]
        except KeyError:
            self.fail(f"clean_url validation error was not raised: {form.errors}")

        self.assertEqual(str(validation_error), "Could not reach target url")

    @passing_clean_url_patch
    def test_successfully_saves_entry_instance(self, clean_url_mock):
        form = EntryForm(self.valid_data)
        entry = form.save()
        self.assertIsNotNone(entry.pk)
        # getting entry from db shouldn't raise errors
        entry = Entry.objects.get(pk=entry.pk)

    @patch("requests.Session.head")
    def test_skips_url_request_on_resave_with_same_url(self, requests_head_mock):
        form = EntryForm(self.valid_data, instance=self.entry)
        form.save()
        requests_head_mock.assert_not_called()

    @patch("requests.Session.head")
    def test_requests_url_on_resave_if_url_changed(self, requests_head_mock):
        mock_response = Response()
        mock_response.url = self.entry.url
        requests_head_mock.return_value = mock_response
        form = EntryForm(self.valid_data)
        form.save()
        requests_head_mock.assert_called_once()
