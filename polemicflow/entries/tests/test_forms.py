from unittest.mock import patch

import requests
from django.test import TestCase
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from ..forms import EntryForm
from ..models import Entry
from .bakery_recipes import entry_recipe
from .common import get_mock_response

fake = Faker()


class EntryFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()
        cls.entry = entry_recipe.make()

    def setUp(self):
        self.label = fake.pystr()
        self.valid_data = {"url": self.entry.url, "label": self.label}
        self.mime_type = fake.mime_type()
        self.valid_head_response = get_mock_response(self.entry.url, self.mime_type)

    @patch("requests.Session.head")
    def test_form_is_valid_when_url_passed(self, head_mock):
        head_mock.return_value = self.valid_head_response
        form = EntryForm(self.valid_data)
        self.assertTrue(form.is_valid())

    @patch("requests.Session.head")
    def test_form_fail_when_invalid_url(self, head_mock):
        head_mock.return_value = self.valid_head_response
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
        head_mock.return_value = self.valid_head_response
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
        head_mock.return_value = self.valid_head_response
        form = EntryForm(self.valid_data)
        form.save()
        head_mock.assert_called_once()
