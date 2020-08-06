from django.contrib import messages
from django.test import TestCase, modify_settings, override_settings
from faker import Faker

fake = Faker()


@override_settings(DEBUG=True)
@modify_settings(
    MIDDLEWARE={"append": "polemicflow.common.middleware.random_debug_message"}
)
class RandomDebugMessageMiddleware(TestCase):
    def test_debug_message_gets_added(self):
        response = self.client.get("/")
        messages_ = messages.get_messages(response.wsgi_request)
        self.assertEqual(len(messages_), 1)

    @override_settings(DEBUG=False)
    def test_message_does_not_get_added_if_not_debug(self):
        response = self.client.get("/")
        messages_ = messages.get_messages(response.wsgi_request)
        self.assertEqual(len(messages_), 0)
