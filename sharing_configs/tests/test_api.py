import json
import os
from email import header
from http.client import HTTPException
from unittest import mock
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from requests.exceptions import ConnectionError, RequestException, Timeout

from sharing_configs.client_util import SharingConfigsClient

from .factories import StaffUserFactory, UserFactory

TEST_DIR = os.path.dirname(os.path.abspath(__file__))  # sharing_configs/tests

User = get_user_model()


class TestImportMixin(TestCase):
    """There are two folders in json file for testing purpose"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        # self.api_config = SharingConfigsClient()

    @patch("sharing_configs.utils.get_folders_from_api")
    def test_call_external_api_from_custom_formfield(self, get_mock_data):
        """
        On request GET three <option></option>'s of "folder"field  will be pre-populated
        with API data- triggered by (custom)field creation
        """
        url = reverse("admin:auth_user_import")
        get_mock_data.return_value = [
            "folder_one",
            "folder_two",
        ]
        resp = self.client.get(url)

        form_folder_field = resp.context["form"]["folder"]
        form_file_name_field = resp.context["form"]["file_name"]
        top_choice_folders_empty = form_folder_field[0]
        top_select_dropdown_value = top_choice_folders_empty.data["value"]
        first_prepopulated_folder = form_folder_field[1]
        first_folder_name = first_prepopulated_folder.data["value"]
        second_prepopulated_folder = form_folder_field[2]
        second_folder_name = second_prepopulated_folder.data["value"]

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["form"].is_bound, False)
        self.assertEqual(3, len(form_folder_field))
        self.assertEqual(0, len(form_file_name_field))
        self.assertEqual(top_select_dropdown_value, "")
        self.assertEqual(first_folder_name, "folder_one")
        self.assertEqual(second_folder_name, "folder_two")
        self.assertTemplateUsed(resp, "sharing_configs/admin/import.html")

    def test_import_valid_form(self):
        """redirect on success"""
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": "bar.txt"}
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)

    def test_import_form_no_file_field(self):
        """if file name not in data, form with error rendered in a template"""
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": ""}
        resp = self.client.post(url, data=data)
        form = resp.context["form"]
        file_field = resp.context["form"].fields["file_name"]
        err_msg = file_field.error_messages.get("required", None)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(form.is_bound, True)
        self.assertEqual(file_field.required, True)
        self.assertEqual(err_msg, "This field is required.")

    @patch("sharing_configs.utils.get_imported_files_choices")
    def test_ajax_correct_data(self, get_mock_data):
        """request returns correct list of files for a given folder"""
        get_mock_data.return_value = ["folder_one.json", "folder_one.html"]
        url = reverse("admin:auth_user_import")
        resp = self.client.post(
            url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            content_type="application/json",
            data={"folder": "folder_one"},
        )
        resp_data = resp.json()
        data = resp_data.get("resp")
        # data ['folder_one.json', 'folder_one.html']
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data, ["folder_one.json", "folder_one.html"])
        self.assertEqual(2, len(data))
