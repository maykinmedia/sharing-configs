from unittest.mock import patch
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest
import requests_mock

from ..client_util import SharingConfigsClient
from ..exceptions import ApiException
from .factories import SharingConfigsConfigFactory, StaffUserFactory

User = get_user_model()


class TestExportMixinPatch(TestCase):
    """Test export mocking 'requests' module"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.config_object = SharingConfigsConfigFactory()
        self.client_api = SharingConfigsClient()

    @patch("sharing_configs.client_util.requests.post")
    def test_ok_request_post(self, mock_post):
        """mocking success during export of an (file)object"""
        expect_dict = {
            "download_url": "http://example.com",
            "filename": "foo.txt",
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "download_url": "http://example.com",
            "filename": "foo.txt",
        }
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

    def test_fail_request_post(self):
        """mocking api failure during export of (file)object"""
        folder = "folder_bar"
        url = urljoin(self.config_object.api_endpoint, self.config_object.label)
        url += f"/folder/{folder}/files/"
        data = {
            "filename": "file.txt",
            "author": str(self.user),
            "content": "some file(object)",
            "overwrite": False,
        }
        with requests_mock.Mocker() as mock_get:
            mock_get.register_uri("POST", url, json=data, status_code=500)
            with pytest.raises(ApiException):
                self.client_api.export(folder, data)
