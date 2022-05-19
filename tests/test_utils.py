import base64

from django.contrib.auth import get_user_model
from django.test import TestCase

from sharing_configs.utils import get_str_from_encoded64_object

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
        result_string = get_str_from_encoded64_object(content)
        self.assertEqual(result_string, "ZXhhbXBsZV9maWxlLnR4dA==")
        self.assertIsInstance(result_string, str)
