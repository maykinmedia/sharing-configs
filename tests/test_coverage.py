from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse

from .factories import StaffUserFactory
from .mock_data_api.mock_util import get_mock_folders

User = get_user_model()


class TestForm(TestCase):
    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)

    @patch("sharing_configs.utils.get_folders_from_api")
    def test_export_form_intials(self, get_mock_data):
        """
        On request GET  export form filename field  should be pre-populated
        with initial data == string representaion of an object
        """
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        initial_for_filename = {"file_name": f"{self.user}.json"}
        get_mock_data.return_value = get_mock_folders("import")
        resp = self.client.get(url)
        initial_from_form = resp.context["form"]["file_name"].value()
        self.assertEqual(resp.context["form"].is_bound, False)
        self.assertEqual(initial_for_filename["file_name"], initial_from_form)
