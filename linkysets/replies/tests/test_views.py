from django.shortcuts import reverse
from django.test import TestCase
from django.utils.http import urlencode
from faker import Faker

from linkysets.entries.tests.bakery_recipes import entryset_recipe

from .. import views
from ..models import Reply
from .bakery_recipes import reply_recipe

fake = Faker()


class PostReplyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entryset = entryset_recipe.make()
        cls.parent_reply = reply_recipe.make(parent=None)

    def setUp(self):
        self.url_reverse = reverse("replies:post")
        query_string = urlencode(
            {"entryset": self.entryset.pk, "reply": self.parent_reply.pk}
        )
        self.url = f"{self.url_reverse}?{query_string}"
        self.parent = self.parent_reply.pk
        self.text = fake.pystr()
        self.valid_data = {"parent": self.parent, "text": self.text}

    def test_correctly_resolves_view(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.resolver_match.func.__name__, views.PostReplyView.as_view().__name__
        )

    def test_get_returns_ok_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "replies/post_reply.html")

    def test_context_has_entryset(self):
        response = self.client.get(self.url)
        self.assertIn("entryset", response.context)
        self.assertEqual(response.context["entryset"].pk, self.entryset.pk)

    def test_context_has_parent_reply(self):
        response = self.client.get(self.url)
        self.assertIn("parent_reply", response.context)
        self.assertEqual(response.context["parent_reply"].pk, self.parent_reply.pk)

    def test_context_parent_reply_is_none(self):
        query_string = urlencode({"entryset": self.entryset.pk})
        response = self.client.get(f"{self.url_reverse}?{query_string}")
        self.assertIsNone(response.context["parent_reply"])

    def test_post_creates_new_reply(self):
        self.client.post(self.url, self.valid_data)
        Reply.objects.get(text=self.text)

    def test_successful_post_redirects_to_entryset_detail(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.entryset.get_absolute_url())

    def test_raises_value_error_if_no_entryset_query_parameter(self):
        with self.assertRaises(ValueError):
            self.client.get(self.url_reverse)

    def test_returns_not_found_if_nonexistent_entryset_pk(self):
        query_string = urlencode({"entryset": fake.pyint()})
        response = self.client.get(f"{self.url_reverse}?{query_string}")
        self.assertEqual(response.status_code, 404)
