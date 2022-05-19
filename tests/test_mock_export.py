from unittest.mock import MagicMock, patch
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse

import requests_mock

from sharing_configs.client_util import SharingConfigsClient
from sharing_configs.exceptions import ApiException

from .factories import SharingConfigsConfigFactory, StaffUserFactory
from .mock_data_api.mock_util import export_api_response, get_mock_folders

User = get_user_model()


class TestExportMixinPatch(TestCase):
    """Test export mocking 'requests' module"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.config_object = SharingConfigsConfigFactory()
        self.client_api = SharingConfigsClient()

        self.url = urljoin(self.config_object.api_endpoint, self.config_object.label)

    @patch("sharing_configs.client_util.requests.post")
    def test_ok_request_post(self, mock_post):
        """mocking success during export of an (file)object"""
        expect_dict = export_api_response()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = export_api_response()
        folder = "folder_one"
        client_api = SharingConfigsClient()
        response_dict = client_api.export(
            folder=folder,
            data={
                "filename": "file.txt",
                "author": str(self.user),
                "content": "some file(object)",
                "overwrite": False,
            },
        )
        mock_post.assert_called_once()
        self.assertEqual(response_dict, expect_dict)

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
    def test_import_valid_form(self, mock_export, get_mock_data_folders):
        """success response if export form valid"""
        mock_export.return_value = {
            "download_url": "http://example.com",
            "filename": "string",
        }
        get_mock_data_folders.return_value = get_mock_folders("export")
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        data = {"folder": "folder_one", "file_name": "foo.txt"}
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)
