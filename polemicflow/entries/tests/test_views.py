from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker

from polemicflow.users.tests.bakery_recipes import user_recipe

from .. import views
from ..models import Entry, Reply
from .bakery_recipes import entry_recipe, reply_recipe
from .common import successful_clean_url_patch

fake = Faker()


class EntryListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entries = entry_recipe.make(_quantity=3)
        cls.entry, *_ = cls.entries

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


class AddEntryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()

    def setUp(self):
        self.entry_url = fake.url()
        self.form_data = {"url": self.entry_url}

    def test_correctly_resolves_view(self):
        response = self.client.get(reverse("entries:add"))
        self.assertEqual(
            response.resolver_match.func.__name__, views.AddEntryView.as_view().__name__
        )

    def test_returns_correct_status_code(self):
        response = self.client.get(reverse("entries:add"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("entries:add"))
        self.assertTemplateUsed(response, "entries/add_entry.html")

    @successful_clean_url_patch
    def test_adds_new_anonymous_entry(self, clean_url_mock):
        self.client.post(reverse("entries:add"), self.form_data)
        try:
            entry = Entry.objects.get(url=self.entry_url)
        except Entry.DoesNotExist:
            self.fail(f"Entry wasn't added using data: {self.form_data}")

        self.assertIsNone(entry._author)

    @successful_clean_url_patch
    def test_adds_new_authored_entry(self, clean_url_mock):
        self.client.force_login(self.user)
        self.client.post(reverse("entries:add"), self.form_data)
        try:
            entry = Entry.objects.get(url=self.entry_url)
        except Entry.DoesNotExist:
            self.fail(
                f'Entry wasn\'t added by user "{self.user}" using data: {self.form_data}'
            )

        self.assertEqual(entry._author, self.user)

    @successful_clean_url_patch
    def test_redirects_to_home_on_success(self, clean_url_mock):
        response = self.client.post(reverse("entries:add"), self.form_data)
        self.assertRedirects(response, reverse("entries:list"))


class EntryDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user_recipe.make()
        cls.entry = entry_recipe.make()
        cls.reply = reply_recipe.make(entry=cls.entry)

    def setUp(self):
        self.reply_text = fake.pystr()
        self.reply_data = {"text": self.reply_text}

    def test_correctly_resolves_view(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertEqual(
            response.resolver_match.func.__name__, views.entry_detail_view.__name__
        )

    def test_get_returns_ok_status_code(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertTemplateUsed(response, "entries/entry_detail.html")

    def test_post_redirects_to_same_entry_detail_page(self):
        url = self.entry.get_absolute_url()
        response = self.client.post(url, self.reply_data)
        self.assertRedirects(response, url)

    def test_returns_not_found_status_code_on_invalid_pk(self):
        pk = fake.pyint()
        response = self.client.get(reverse("entries:detail", args=(pk,)))
        self.assertEqual(response.status_code, 404)

    def test_posts_anonymous_reply(self):
        self.client.post(self.entry.get_absolute_url(), self.reply_data)
        reply = Reply.objects.get(entry=self.entry.pk, text=self.reply_text)
        self.assertIsNone(reply._author)

    def test_posts_authored_reply(self):
        self.client.force_login(self.user)
        self.client.post(self.entry.get_absolute_url(), self.reply_data)
        reply = Reply.objects.get(entry=self.entry.pk, text=self.reply_text)
        self.assertEqual(reply._author, self.user)

    def test_posts_direct_reply(self):
        self.client.post(self.entry.get_absolute_url(), self.reply_data)
        reply = Reply.objects.get(entry=self.entry.pk, text=self.reply_text)
        self.assertIsNone(reply.parent)

    def test_posts_child_reply(self):
        self.client.post(
            self.entry.get_absolute_url(), {"parent": self.reply.pk, **self.reply_data},
        )
        reply = Reply.objects.get(
            entry=self.entry.pk, parent=self.reply.pk, text=self.reply_text
        )
        self.assertEqual(reply.parent.pk, self.reply.pk)
