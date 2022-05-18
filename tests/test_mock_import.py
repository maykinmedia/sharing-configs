from http import HTTPStatus
from unittest import mock
from unittest.mock import patch
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse

import requests_mock

from sharing_configs.client_util import SharingConfigsClient
from sharing_configs.exceptions import ApiException

from .factories import SharingConfigsConfigFactory, StaffUserFactory
from .mock_data_api.mock_util import get_mock_folders

User = get_user_model()


class TestImportMixinPatchFuncs(TestCase):
    """Test import mocking utils functions"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)

    @patch("sharing_configs.utils.get_folders_from_api")
    def test_call_external_api_from_form(self, get_mock_data):
        """
        On request GET "folder" form field  will be pre-populated
        with mocked API data
        """
        url = reverse("admin:auth_user_import")
        get_mock_data.return_value = get_mock_folders("import")
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
        # TODO: create dispatch
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

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    def test_import_valid_form(self, get_mock_data):
        """success response if import form valid"""
        get_mock_data.return_value = get_mock_folders("import")
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        resp = self.client.get(url, json=data)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    def test_fail_import_form_without_file(self, get_mock_data):
        """if file name not in data, form with error message rendered in a template"""
        url = reverse("admin:auth_user_import")
        get_mock_data.return_value = get_mock_folders("import")

        data = {"folder": "folder_one", "file_name": ""}
        resp = self.client.post(url, data=data)
        form = resp.context["form"]
        file_field = resp.context["form"].fields["file_name"]
        err_msg = file_field.error_messages.get("required", None)
        self.assertEqual(form.is_bound, True)
        self.assertEqual(file_field.required, True)
        self.assertEqual(err_msg, "This field is required.")


class TestImportMixinRequestsMock(TestCase):
    """Test import mocking module 'requests' on success and failure in util functions"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.config_object = SharingConfigsConfigFactory()
        self.client_api = SharingConfigsClient()
        self.folder = "folder_one"
        self.filename = "test.txt"
        self.url = urljoin(self.config_object.api_endpoint, self.config_object.label)

    @patch("sharing_configs.client_util.requests.get")
    def test_ok_request_get_from_form(self, mock_get):
        """API call success in fetching list of folders"""
        value = get_mock_folders("import")
        self.url += "/folder/"
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = value
        resp_dict = self.client_api.get_folders(permission=None)
        self.assertTrue(mock_get.called)
        self.assertEqual(resp_dict, value)

    @patch("sharing_configs.client_util.requests.get")
    def test_ok_get_files_from_api(self, mock_get):
        """API call success in fetching data with files"""
        folder = "collection"
        return_value = ["folder_one.json", "folder_one.html"]
        self.url += f"/folder/{folder}/files/"
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = return_value
        response = self.client_api.get_files(folder)
        self.assertTrue(mock_get.called)
        self.assertEqual(response, return_value)

    @patch("sharing_configs.client_util.requests.get")
    def test_ok_request_get_import_data(self, mock_get):
        """Import object successfull; return value is a binary"""
        return_value = b"example_file.txt"
        self.url += f"/folder/{self.folder}/files/{self.filename}"
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = return_value
        resp_str = self.client_api.import_data(self.folder, self.filename)
        self.assertTrue(mock_get.called)
        self.assertEqual(resp_str, b"example_file.txt")

    # @tag("deze")
    def test_failed_fetch_folders_via_form_init(self):
        """API call failed to fetch list of folders: list of folders empty"""

        url = self.client_api.get_list_folders_url()
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("GET", url, json={}, status_code=500)

            with self.assertRaises(ApiException):
                self.client_api.get_folders(permission=None)
