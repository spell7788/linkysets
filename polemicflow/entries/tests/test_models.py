from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from .bakery_recipes import anonymous_entry_recipe, entry_recipe


class EntriesTests(TestCase):
    def setUp(self):
        self.entry = entry_recipe.make()
        self.entry_author = self.entry.author
        self.anonymous_entry = anonymous_entry_recipe.make()

    def test_entry_has_existing_author(self):
        self.assertNotIsInstance(self.entry.author, AnonymousUser)

    def test_anonymous_entry_has_anonymous_author(self):
        self.assertIsInstance(self.anonymous_entry.author, AnonymousUser)

    def test_author_becomes_anonymous_after_user_deletion(self):
        self.entry_author.delete()
        self.entry.refresh_from_db(fields=["_author"])
        self.assertIsInstance(self.entry.author, AnonymousUser)
