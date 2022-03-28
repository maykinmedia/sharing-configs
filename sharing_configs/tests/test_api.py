import json
import os
from email import header
from http.client import HTTPException
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from requests.exceptions import ConnectionError, RequestException, Timeout

from .factories import UserFactory

TEST_DIR = os.path.dirname(os.path.abspath(__file__))  # sharing_configs/tests


class TestExternalAPI(TestCase):
    # def setUp(self) -> None:
    #     self.api_config = None # ConfigConfigs..

    @patch("sharing_configs.fields.get_imported_folders_choices")
    def test_call_external_api(self, get_mock_data):
        url = reverse("admin:auth_user_import")
        response = self.client.post(
            url, HTTP_X_REQUESTED_WITH="XMLHttpRequest", content_type="application/json"
        )
        try:
            with open(os.path.join(TEST_DIR, "mock_data/folders.json")) as fh:
                get_mock_data.return_value = json.load(fh)["data"]
                get_mock_data.return_value = [
                    "folder_one",
                    "folder_two",
                    "folder_three",
                ]
                self.assertEqual(response.status_code, 302)

        except:
            get_mock_data.side_effect = [
                ConnectionError,
                Timeout,
                HTTPError,
                RequestException,
            ]
            self.assertRaises(Exception, get_mock_data)
