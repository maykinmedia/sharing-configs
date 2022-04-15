from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import requests

from ..client_util import SharingConfigsClient
from ..models import SharingConfigsConfig
from .factories import StaffUserFactory

User = get_user_model()


class TestImportMixinPatchFuncs(TestCase):
    """Test import mocking utils functions"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)

    @patch("sharing_configs.utils.get_folders_from_api")
    def test_call_external_api_from_from(self, get_mock_data):
        """
        On request GET "folder" form field  will be pre-populated
        with mocked API data
        """
        url = reverse("admin:auth_user_import")
        get_mock_data.return_value = {
            "count": 123,
            "next": "http://api.example.org/accounts/?page=4",
            "previous": "http://api.example.org/accounts/?page=2",
            "results": [
                {"name": "folder_one", "children": []},
                {"name": "folder_two", "children": []},
            ],
        }
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

    @patch("sharing_configs.utils.get_files_in_folder_from_api")
    def test_ajax_correct_data(self, get_mock_data):
        """utils function returns correct list of files for a given folder"""
        get_mock_data.return_value = {
            "count": 123,
            "next": "http://api.example.org/accounts/?page=4",
            "previous": "http://api.example.org/accounts/?page=2",
            "results": [
                {"filename": "folder_one.json", "download_url": "http://example.com"},
                {"filename": "folder_one.html", "download_url": "http://example.com"},
            ],
        }
        url = reverse("admin:auth_user_ajax") + str("?folder_name=folder_one")
        resp = self.client.get(
            url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            content_type="application/json",
        )
        resp_data = resp.json()
        data = resp_data.get("resp")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data, ["folder_one.json", "folder_one.html"])
        self.assertEqual(2, len(data))


#     # TODO: if NOT correct
class TestImportMixinPatchRequests(TestCase):
    """Test import mocking module 'requests' in util functions"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.api_client = SharingConfigsConfig.get_solo()
        self.client_api = SharingConfigsClient()

    @patch("sharing_configs.client_util.requests.get")
    def test_ok_request_get_from_form(self, mock_get):
        """API call success: get list of folders"""
        expect_dict = {
            "results": [
                {"name": "folder_one", "children": []},
                {"name": "folder_two", "children": []},
            ],
            "count": 12,
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = expect_dict
        response_dict = self.client_api.get_folders(permission={"permission": "read"})
        self.assertEqual(response_dict, expect_dict)
        mock_get.assert_called_once()

    @patch("sharing_configs.client_util.requests.get")
    def test_failed_request_get_from_form(self, mock_get):
        """API call failed: list of folders empty"""
        expect_dict = {}
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.side_effect = requests.exceptions.RequestException()
        response_dict = self.client_api.get_folders(permission={"permission": "read"})
        self.assertEqual(response_dict, expect_dict)
        mock_get.assert_called_once()
        # TODO: check resp from API

    @patch("sharing_configs.client_util.requests.get")
    def test_ok_request_get_import_data(self, mock_get):
        """Import object successfull"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "msg": "Import successful.Binary here"
        }
        folder = "folder_one"
        filename = "test.txt"
        response_str = self.client_api.import_data(folder, filename)
        mock_get.assert_called_once()
        self.assertEqual(response_str, {"msg": "Import successful.Binary here"})

    @patch("sharing_configs.client_util.requests.get")
    def test_failed_request_get_import_data(self, mock_get):
        """API request get failed to fetch object"""
        folder = "folder_one"
        filename = "test.txt"
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.side_effect = requests.exceptions.RequestException()
        response = self.client_api.import_data(folder, filename)
        mock_get.assert_called_once()
        self.assertEqual(response, {})
