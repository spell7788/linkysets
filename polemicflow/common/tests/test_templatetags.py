# flake8: noqa: E800
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from faker import Faker

fake = Faker()


class TransformQueryTests(TestCase):
    def setUp(self):
        self.param_key = fake.pystr()
        self.param_value = fake.pystr()
        self.request = RequestFactory().get("/", {self.param_key: self.param_value})

    def test_adds_new_parameter(self):
        param_key = fake.pystr()
        param_value = fake.pystr()
        # fmt: off
        out = Template(
            "{% load common_tags %}"
            f"{{% transform_query {param_key}='{param_value}' %}}"
        ).render(Context({"request": self.request}, autoescape=False))
        # fmt: on
        self.assertEqual(
            out, f"{self.param_key}={self.param_value}&{param_key}={param_value}"
        )

    def test_overrides_existing_parameter(self):
        new_value = fake.pystr()
        # fmt: off
        out = Template(
            "{% load common_tags %}"
            f"{{% transform_query {self.param_key}='{new_value}' %}}"
        ).render(Context({"request": self.request}, autoescape=False))
        # fmt: on
        self.assertEqual(out, f"{self.param_key}={new_value}")
