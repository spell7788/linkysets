from django.core.exceptions import ValidationError
from django.test import TestCase

from .bakery_recipes import entryset_recipe


class EntrySetTests(TestCase):
    def setUp(self):
        self.entryset = entryset_recipe.make(_fill_optional=True)

    def test_str_returns_set_name_if_name_is_presented(self):
        self.assertEqual(str(self.entryset), self.entryset.name)

    def test_clean_raises_validation_error_when_no_entries(self):
        self.entryset.entries.clear()
        with self.assertRaises(ValidationError):
            self.entryset.clean()

    def test_gets_correct_author(self):
        self.assertEqual(self.entryset.get_author().pk, self.entryset.author.pk)

    def test_gets_anonymous_author(self):
        self.entryset.author = None
        self.entryset.save()
        self.assertIsNone(self.entryset.get_author().pk)
