from http import HTTPStatus
from unittest.mock import patch
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import pytest
import requests_mock

from ..client_util import SharingConfigsClient
from ..exceptions import ApiException
from ..models import SharingConfigsConfig
from .factories import SharingConfigsConfigFactory, StaffUserFactory

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

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    def test_import_valid_form(self, get_mock_data):
        """success response if import form valid"""
        get_mock_data.return_value = {
            "count": 123,
            "next": "http://api.example.org/accounts/?page=4",
            "previous": "http://api.example.org/accounts/?page=2",
            "results": [
                {
                    "name": "string",
                    "children": [{"name": "string", "children": []}],
                    "permission": "read",
                }
            ],
        }
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        resp = self.client.get(url, json=data)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    def test_fail_import_form_without_file(self, get_mock_data):
        """if file name not in data, form with error message rendered in a template"""
        url = reverse("admin:auth_user_import")
        get_mock_data.return_value = {
            "count": 123,
            "next": "http://api.example.org/accounts/?page=4",
            "previous": "http://api.example.org/accounts/?page=2",
            "results": [
                {
                    "name": "string",
                    "children": [{"name": "string", "children": []}],
                    "permission": "read",
                }
            ],
        }
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

    @requests_mock.Mocker()
    def test_ok_request_get_from_form(self, mock_get):
        """API call success in fetching list of folders"""
        return_value = {
            "count": 123,
            "next": "http://api.example.org/accounts/?page=4",
            "previous": "http://api.example.org/accounts/?page=2",
            "results": [
                {
                    "name": "string",
                    "children": [{"name": "string", "children": []}],
                    "permission": "read",
                }
            ],
        }
        url = urljoin(self.config_object.api_endpoint, self.config_object.label)
        url += "/folder/?permission=read"
        mock_get.get(url=url, json=return_value, status_code=200)
        response = self.client_api.get_folders(permission={"permission": "read"})
        self.assertTrue(mock_get.called)
        self.assertEqual(response, return_value)

    @requests_mock.Mocker()
    def test_ok_get_files_from_api(self, mock_get):
        """API call success in fetching data with files"""
        folder = "collection"
        return_value = ["folder_one.json", "folder_one.html"]
        url = urljoin(self.config_object.api_endpoint, self.config_object.label)
        url += f"/folder/{folder}/files/"
        mock_get.get(url=url, json=return_value, status_code=200)
        response = self.client_api.get_files(folder)
        self.assertTrue(mock_get.called)
        self.assertEqual(response, return_value)

    @requests_mock.Mocker()
    def test_ok_request_get_import_data(self, mock_get):
        """Import object successfull"""
        return_value = {"msg": "Import successful.Binary here"}
        folder = "folder_one"
        filename = "test.txt"
        url = urljoin(self.config_object.api_endpoint, self.config_object.label)
        url += f"/folder/{folder}/files/{filename}/"
        mock_get.get(url=url, json=return_value, status_code=200)
        resp_str = self.client_api.import_data(folder, filename)
        self.assertTrue(mock_get.called)
        self.assertEqual(resp_str, {"msg": "Import successful.Binary here"})

    def test_failed_request_get_import_data(self):
        """API request-get failed to fetch object"""
        folder = "folder_one"
        filename = "test.txt"
        url = urljoin(self.config_object.api_endpoint, self.config_object.label)
        url += f"/folder/{folder}/files/{filename}/"
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("GET", url, json={}, status_code=500)
            with pytest.raises(ApiException):
                self.client_api.import_data(folder, filename)

    def test_failed_fetch_folders_via_form_init(self):
        """API call failed to fetch list of folders: list of folders empty"""
        url = urljoin(self.config_object.api_endpoint, self.config_object.label)
        url += "/folder/?permission=read"
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("GET", url, json={}, status_code=500)
            with pytest.raises(ApiException):
                self.client_api.get_folders(permission={"permission": "read"})

        # TODO: to get feedback from a reviewer about a bug in my tests
        # code returns json {'msg': 'Import successful.Binary here'} instead of raising exception
        # Option N 1
        # utittest.mock  patch doesn't work (see below requests_mock)
        # @patch("sharing_configs.client_util.requests.get")
        # def test_failed_request_get_import_data(self, mock_get):
        #     """API request-get failed to fetch object"""
        #     # test target 1: check of status_code == 500
        #     # test target 2: check folder list = []
        #     folder = "folder_one"
        #     filename = "test.txt"
        #     mock_get.return_value.status_code = 500
        #     mock_get.get.return_value.raise_for_status.side_effect = [
        #         requests.exceptions.HTTPError(),
        #     ]

        #     mock_get.get.return_value.json.return_value = None
        #     response = self.client_api.import_data(folder, filename)
        #     # response.raise_for_status()
        #     mock_get.assert_called_once()
        #     self.assertEqual(response.status_code, 500)
        #################################################
        # Option N 2
        # TODO: this approach doesn't work either
        # with self.assertRaises(ApiException) as exc:
        #     # get errot AttributeError: '_AssertRaisesContext' object has no attribute 'exception'
        #     response = self.client_api.import_data(folder, filename)
        #     assert "requests.exceptions.HTTPError" in exc.exception

        # N 2 requests_mock doesn't work either for me
        # TODO: I see the same bug in this code as with unittests.mock patch: return json instead of raising an exception
        # @requests_mock.Mocker()
        # def test_failed_request_get_from_form(self, mock_get):
        #     """API call failed to fetch list of folders: list of folders empty"""
        #     url = urljoin(self.config_object.api_endpoint, self.config_object.label)
        #     url += "/folder/?permission=read"
        #     mock_get.get(url=url, exc=requests.exceptions.HTTPError) # also impossible to add status_code as a param
        #     response = self.client_api.get_folders(permission={"permission": "read"})
        #     response.raise_for_status()
        #     self.assertTrue(mock_get.called)
        #     self.assertTrue(mock_get.call_count)
        #     self.assertRaises(requests.exceptions.HTTPError) #or ApiException
