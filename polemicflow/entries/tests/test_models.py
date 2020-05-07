from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from ..models import Entry


class EntriesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anonymous_entry = Entry.objects.create(url="https://example.com")

    def test_anon_author_of_anon_entry(self):
        self.assertIsInstance(self.anonymous_entry.author, AnonymousUser)
