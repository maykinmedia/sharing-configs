from django.test import TestCase

from sharing_configs.utils import get_str_from_encoded64_object


class TestUtils(TestCase):
    def test_convertion_encoded64_obj_to_string(self):
        """test func get_str_from_encoded64_object if it return a string after base
        64-encoding of a byte-like object"""
        content = b"example_file.txt"
        result_string = get_str_from_encoded64_object(content)

        self.assertEqual(result_string, "ZXhhbXBsZV9maWxlLnR4dA==")
        self.assertIsInstance(result_string, str)
