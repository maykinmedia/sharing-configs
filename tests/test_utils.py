import base64

from django.contrib.auth import get_user_model
from django.test import TestCase

from .factories import StaffUserFactory

User = get_user_model()


class TestUtils(TestCase):
    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)

    def test_convertion_encoded64_obj_to_string(self):
        """test func get_str_from_encoded64_object if it return a string after base
        64-encoding of a byte-like object"""
        content = b"example_file.txt"
        decoded_base64_encoded_string = base64.b64encode(content).decode("utf-8")

        self.assertEqual(decoded_base64_encoded_string, "ZXhhbXBsZV9maWxlLnR4dA==")
        self.assertIsInstance(decoded_base64_encoded_string, str)
