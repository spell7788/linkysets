from django.shortcuts import reverse
from django.test import TestCase

from .. import views
from ..models import Entry


class EntryListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entry = Entry.objects.create(url="https://example.com")

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
