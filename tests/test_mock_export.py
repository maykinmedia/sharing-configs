from unittest.mock import patch
from urllib.parse import urljoin

from django.test import TestCase
from django.urls import reverse

import requests_mock

from sharing_configs.client_util import SharingConfigsClient
from sharing_configs.exceptions import ApiException

from .factories import SharingConfigsConfigFactory, StaffUserFactory
from .mock_data_api.mock_util import export_api_response, get_mock_folders


class TestExportMixinPatch(TestCase):
    """Test export mocking 'requests' module"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.config_object = SharingConfigsConfigFactory()
        self.client_api = SharingConfigsClient()

        self.url = urljoin(self.config_object.api_endpoint, self.config_object.label)

    @requests_mock.Mocker()
    def test_ok_request_post(self, mock_post):
        """mocking success during export of an (file)object"""
        expect_dict = export_api_response()
        folder = "folder_one"
        data = {
            "filename": "file.txt",
            "author": str(self.user),
            "content": "some file(object)",
            "overwrite": False,
        }
        url = self.client_api.get_export_url(folder=folder)
        mock_post.post(url, json=expect_dict)
        response = self.client_api.export(folder="folder_one", data=data)
        self.assertTrue(mock_post.called)
        self.assertEqual(response, expect_dict)

    def test_failed_fetch_folders_via_form_init(self):
        """API call failed to fetch list of folders: list of folders empty"""

        url = self.client_api.get_list_folders_url()
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("GET", url, json={}, status_code=500)
            with self.assertRaises(ApiException):
                self.client_api.get_folders(permission=None)

    def test_fail_request_post(self):
        """mocking api failure during export of (file)object"""
        folder = "folder_bar"
        url = self.client_api.get_export_url(folder=folder)
        data = {
            "filename": "file.txt",
            "author": str(self.user),
            "content": "some file(object)",
            "overwrite": False,
        }
        with requests_mock.Mocker() as mock_post:
            mock_post.register_uri("POST", url, json=data, status_code=500)

            with self.assertRaises(ApiException):
                self.client_api.export(folder, data)

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    @patch("sharing_configs.client_util.SharingConfigsClient.export")
    def test_export_valid_form(self, mock_export, get_mock_data_folders):
        """if export form valid response success and re-direct to the same export url"""
        mock_export.return_value = {
            "download_url": "http://example.com",
            "filename": "string",
        }
        get_mock_data_folders.return_value = get_mock_folders("export")
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        data = {"folder": "folder_one", "file_name": "foo.txt"}
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, url, status_code=302, target_status_code=200)

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

    @patch("sharing_configs.client_util.requests.get")
    def test_query_params_requesting_list_folders_for_export(self, mock_get):
        """permissions in query params present to get list of available folders in export"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {
            "content-type": "application/json",
            "authorization": self.config_object.api_key,
        }
        url = self.client_api.get_list_folders_url()
        resp = self.client_api.get_folders(permission="write")
        mock_get.assert_called_once_with(
            url=url,
            headers={
                "content-type": "application/json",
                "authorization": self.config_object.api_key,
            },
            params="write",
        )
