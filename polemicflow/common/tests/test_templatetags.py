from django.conf import settings
from django.test import TestCase
from django.utils import translation

from polemicflow.entries.tests.bakery_recipes import entryset_recipe

from ..templatetags import common_tags as tags


class GetUsernameTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entryset = entryset_recipe.make()
        cls.entryset_author = cls.entryset.get_author()
        cls.anonymous_entryset = entryset_recipe.make(author=None)

    def test_returns_correct_entryset_author_username(self):
        username = tags.get_username(self.entryset)
        self.assertEqual(username, self.entryset_author.username)

    def test_returns_anonymous_username_for_anonymous_user(self):
        username = tags.get_username(self.anonymous_entryset)
        with translation.override(None, deactivate=True):
            self.assertEqual(username, settings.ANONYMOUS_USERNAME)

    def test_returns_lazy_anonymous_username(self):
        username = tags.get_username(self.anonymous_entryset)
        self.assertEqual(type(username).__name__, "__proxy__")
