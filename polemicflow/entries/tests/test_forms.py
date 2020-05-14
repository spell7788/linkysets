from django.test import TestCase
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from ..forms import EntryForm
from .common import failing_clean_url_patch, successful_clean_url_patch

fake = Faker()


class EntryFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()

    def setUp(self):
        self.url = fake.url()

    @successful_clean_url_patch
    def test_form_is_valid_when_url_passed(self, clean_url_mock):
        form = EntryForm(data={"url": self.url})
        self.assertTrue(form.is_valid())

    @successful_clean_url_patch
    def test_form_invalid_when_not_url_passed(self, clean_url_mock):
        form = EntryForm(data={"url": fake.pystr()})
        self.assertFalse(form.is_valid())

    @failing_clean_url_patch
    def test_clean_url_raises_validation_error(self, clean_url_mock):
        form = EntryForm(data={"url": self.url})
        self.assertFalse(form.is_valid())
        try:
            validation_error = form.errors["url"][0]
        except KeyError:
            self.fail(f"clean_url validation error was not raised: {form.errors}")

        self.assertEqual(str(validation_error), "Could not reach target url")

    @successful_clean_url_patch
    def test_form_saves_entry_author_if_presented(self, clean_url_mock):
        form = EntryForm(self.user, {"url": self.url})
        entry = form.save()
        self.assertEqual(entry._author, self.user)
