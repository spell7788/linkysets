from django.core.exceptions import ValidationError
from django.test import TestCase
from faker import Faker

from .. import behavior
from ..models import Entry
from .bakery_recipes import entry_recipe, entryset_recipe
from .common import get_random_youtube_url

fake = Faker()


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


class EntryTests(TestCase):
    def setUp(self):
        self.entry = entry_recipe.prepare()

    def test_correctly_determines_only_mime_dependent_types(self):
        exclude_types = [Entry.EntryType.YT_VIDEO, Entry.EntryType.URL]
        types = (
            (type_, behavior_cls)
            for type_, behavior_cls in Entry._TYPE_BEHAVIOR_DICT.items()
            if type_ not in exclude_types
        )

        for type_, behavior_cls in types:
            url = fake.url()
            mime_type = fake.random_element(behavior_cls.mime_types)
            with self.subTest(type_=type_, url=url, mime_type=mime_type):
                self.assertEqual(type_, self.entry.determine_type(url, mime_type))

    def test_correctly_determines_youtube_type(self):
        url = get_random_youtube_url()
        mime_type = fake.random_element(behavior.YtVideoTypeBehavior.mime_types)
        type_ = self.entry.determine_type(url, mime_type)
        self.assertEqual(type_, Entry.EntryType.YT_VIDEO)

    def test_correctly_determines_url_type(self):
        url = fake.url()
        type_ = self.entry.determine_type(url, "text/html")
        self.assertEqual(type_, Entry.EntryType.URL)

    def test_gets_correct_type_behavior(self):
        for type_, behavior_cls in Entry._TYPE_BEHAVIOR_DICT.items():
            self.entry.type = type_
            with self.subTest(type=type_, behavior_cls=behavior_cls):
                self.assertIsInstance(self.entry.type_behavior, behavior_cls)

    def test_correctly_renders_types(self):
        exclude_types = [Entry.EntryType.YT_VIDEO]
        types = (
            (type_, behavior_cls)
            for type_, behavior_cls in Entry._TYPE_BEHAVIOR_DICT.items()
            if type_ not in exclude_types
        )

        for type_, behavior_cls in types:
            self.entry.type = type_
            with self.subTest(type=type_, behavior_cls=behavior_cls):
                html = self.entry.render()
                self.assertIn(self.entry.url, html)

    def test_correctly_renders_youtube_type(self):
        self.entry.url = get_random_youtube_url()
        self.entry.type = Entry.EntryType.YT_VIDEO
        html = self.entry.render()
        self.assertRegex(html, r"https://www\.youtube\.com/embed/\w+")
