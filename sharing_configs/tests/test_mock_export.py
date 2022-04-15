from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import requests

from ..client_util import SharingConfigsClient
from ..models import SharingConfigsConfig
from .factories import StaffUserFactory

User = get_user_model()


class TestExportMixinPatch(TestCase):
    """Test export mocking 'requests' module"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.api_client = SharingConfigsConfig.get_solo()
        self.client_api = SharingConfigsClient()

    @patch("sharing_configs.client_util.requests.post")
    def test_ok_request_post(self, mock_post):
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

    @patch("sharing_configs.client_util.requests.post")
    def test_fail_request_post(self, mock_post):
        expect_dict = {}
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.side_effect = requests.exceptions.RequestException()

        folder = "folder_bar"
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
