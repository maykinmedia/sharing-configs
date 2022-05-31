import json
from http import HTTPStatus
from unittest.mock import patch
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import requests
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
        resp = self.client.post(url, json=data)
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        get_mock_data.assert_called_once_with(None)

    @patch(
        "sharing_configs.client_util.SharingConfigsClient.get_folders",
        return_value=get_mock_folders("import"),
    )
    def test_fail_import_form_without_file(self, get_mock_data):
        """if file name not in data, form with error message rendered in a template"""
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": ""}
        resp = self.client.post(url, data=data)
        form = resp.context["form"]
        file_field = resp.context["form"].fields["file_name"]
        err_msg = file_field.error_messages.get("required", None)
        self.assertEqual(form.is_bound, True)
        self.assertEqual(file_field.required, True)
        self.assertEqual(err_msg, "This field is required.")
        get_mock_data.assert_called_once_with(None)

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    @patch("sharing_configs.client_util.SharingConfigsClient.import_data")
    def test_import_valid_form(self, mock_import, get_mock_data_folders):
        """if import form valid success response and redirect to the same import url;
        (mock)get_folders method also called by re-direct to supply template dropdown-menu with folders
        """
        mock_import.return_value = b"some-words"
        get_mock_data_folders.return_value = get_mock_folders("import")
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, url, status_code=302, target_status_code=200)
        get_mock_data_folders.assert_called_with(None)
        self.assertEqual(get_mock_data_folders.call_count, 2)


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

    @requests_mock.Mocker()
    def test_ok_list_folders_from_form_init(self, mock_get):
        """API call success in fetching list of folders"""
        value = get_mock_folders("import")
        url = self.client_api.get_list_folders_url()
        mock_get.get(url=url, json=value, status_code=200)
        resp = self.client_api.get_folders(permission=None)
        self.assertTrue(mock_get.called)
        self.assertEqual(resp, value)

    @requests_mock.Mocker()
    def test_ok_get_files_from_api(self, mock_get):
        """API call success in fetching list of available files"""
        folder = "folder_one"
        return_value = ["folder_one.json", "folder_one.html"]
        url = self.client_api.get_folder_files_url(folder=folder)
        mock_get.get(url=url, json=return_value, status_code=200)
        response = self.client_api.get_files(folder="folder_one")
        self.assertTrue(mock_get.called)
        self.assertEqual(response, return_value)

    def test_failed_fetch_folders_via_form_init(self):
        """API call failed with error 500 on request to fetch list of folders: list of folders empty"""

        url = self.client_api.get_list_folders_url()
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("GET", url, json={}, status_code=500)

            with self.assertRaises(ApiException):
                self.client_api.get_folders(permission=None)

    def test_failed_404_fetch_files_for_import(self):
        """Client makes incorrect request to fetch list of files"""

        url = self.client_api.get_folder_files_url(folder="myfolder")
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("GET", url, json={}, status_code=404)

            with self.assertRaises(ApiException):
                self.client_api.get_files(folder="myfolder")

    def test_failed_500_fetch_files_for_import(self):
        """API call failed to fetch list of files"""

        url = self.client_api.get_folder_files_url(folder="myfolder")
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("GET", url, json={}, status_code=500)

            with self.assertRaises(ApiException):
                self.client_api.get_files(folder="myfolder")

    @requests_mock.Mocker()
    def test_ok_request_get_import_data(self, mock_get):
        """Import object successfull; return value is a binary"""
        return_value = b"some-string"
        url = self.client_api.get_import_url(self.folder, self.filename)
        mock_get.get(url=url, content=return_value, status_code=200)
        resp = self.client_api.import_data(self.folder, self.filename)
        self.assertTrue(mock_get.called)
        self.assertEqual(resp, return_value)

    @patch("sharing_configs.client_util.requests.get")
    def test_query_params_list_folders_for_import(self, mock_get):
        """no permissions in query params to get list of available folders in import"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {
            "content-type": "application/json",
            "authorization": self.config_object.api_key,
        }
        url = self.client_api.get_list_folders_url()
        resp = self.client_api.get_folders(permission=None)
        mock_get.assert_called_once_with(
            url=url,
            headers={
                "content-type": "application/json",
                "authorization": f"Token {self.config_object.api_key}",
            },
        )

    @patch("sharing_configs.client_util.SharingConfigsClient.import_data")
    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    def test_network_problem_import(self, mock_import_data, mocked_folders):
        """if connection problem occures a generic error message displayed on import template"""
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        mock_import_data.side_effect = requests.exceptions.ConnectionError
        mocked_folders.return_value = {}
        url = reverse("admin:auth_user_import")
        resp = self.client.post(url, data=data)
        messages = list(resp.context["messages"])
        self.assertEqual(str(messages[0]), "Something went wrong during object import")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed("admin/import.html")
