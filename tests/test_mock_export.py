import json
from unittest.mock import patch
from urllib.parse import urljoin

from django.forms.models import model_to_dict
from django.test import TestCase
from django.urls import reverse

import requests
import requests_mock

from sharing_configs.client_util import SharingConfigsClient
from sharing_configs.exceptions import ApiException
from sharing_configs.utils import get_str_from_encoded64_object

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

    def test_fail_500_request_post(self):
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
    @patch("sharing_configs.client_util.requests.post")
    def test_export_valid_form(self, mock_export_data, mocked_folders):
        """if export form valid response success and re-direct to the same export url;
        (mock)get_folders method also called by re-direct to supply template dropdown-menu with folders"""
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        mock_export_data.raise_for_status = 200
        mock_export_data.json.return_value = {
            "download_url": "http://example.com",
            "filename": "string",
        }
        mocked_folders.return_value = get_mock_folders(mode="export")
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        user_dict = model_to_dict(self.user)
        dump_json_user = json.dumps(user_dict, sort_keys=True, default=str)
        byte_user_content = dump_json_user.encode("utf-8")
        content = get_str_from_encoded64_object(byte_user_content)
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, url, status_code=302, target_status_code=200)
        self.assertTrue(mock_export_data.called)
        self.assertTemplateUsed("admin/export.html")
        mocked_folders.assert_called_with("write")
        self.assertEqual(mocked_folders.call_count, 2)
        self.assertTrue(mock_export_data.called)
        mock_export_data.assert_called_once_with(
            url=self.client_api.get_export_url("folder_one"),
            headers={
                "content-type": "application/json",
                "authorization": f"Token {self.config_object.api_key}",
            },
            json={
                f"overwrite": False,
                "content": content,
                "author": str(self.user),
                "filename": data["file_name"],
            },
        )

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
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
        get_mock_data.assert_called_with("write")
        self.assertEqual(get_mock_data.call_count, 1)
        get_mock_data.assert_called_with("write")

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
                "authorization": f"Token {self.config_object.api_key}",
            },
            params="write",
        )

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    def test_fail_export_form_without_file(self, get_mock_data):
        """if file name not in data, form with error message rendered in a template"""
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        get_mock_data.return_value = get_mock_folders("export")
        data = {"folder": "folder_one", "file_name": ""}
        resp = self.client.post(url, data=data)
        form = resp.context["form"]
        file_field = resp.context["form"].fields["file_name"]
        err_msg = file_field.error_messages.get("required", None)
        self.assertEqual(form.is_bound, True)
        self.assertEqual(file_field.required, True)
        self.assertEqual(err_msg, "This field is required.")
        get_mock_data.assert_called_once_with("write")

    @patch("sharing_configs.client_util.SharingConfigsClient.get_folders")
    @patch("sharing_configs.client_util.requests.post")
    def test_partial_network_problem_export(self, mock_export_data, mocked_folders):
        """if connection problem occures a generic error message displayed on export template"""

        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        mock_export_data.side_effect = requests.exceptions.ConnectionError
        mocked_folders.return_value = get_mock_folders(mode="export")
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        resp = self.client.post(url, data=data)
        user_dict = model_to_dict(self.user)
        dump_json_user = json.dumps(user_dict, sort_keys=True, default=str)
        byte_user_content = dump_json_user.encode("utf-8")
        content = get_str_from_encoded64_object(byte_user_content)
        messages = list(resp.context["messages"])
        self.assertTrue(mock_export_data.called)
        self.assertEqual(str(messages[0]), "Export of object failed")
        self.assertTemplateUsed("admin/export.html")
        mocked_folders.assert_called_once_with("write")
        self.assertTrue(mock_export_data.called)
        mock_export_data.assert_called_once_with(
            url=self.client_api.get_export_url("folder_one"),
            headers={
                "content-type": "application/json",
                "authorization": f"Token {self.config_object.api_key}",
            },
            json={
                f"overwrite": False,
                "content": content,
                "author": str(self.user),
                "filename": data["file_name"],
            },
        )

    @patch("sharing_configs.client_util.SharingConfigsClient.export")
    @patch("sharing_configs.client_util.requests.get")
    def test_total_network_problem_export(self, mocked_folders, mock_export_data):
        """if connection problem occures not only during export data but also during fetching folders a generic error message displayed on export template"""
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        url_list_folders = self.client_api.get_list_folders_url()
        mock_export_data.side_effect = requests.exceptions.ConnectionError
        mocked_folders.side_effect = requests.exceptions.ConnectionError
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        resp = self.client.post(url, data=data)
        messages = list(resp.context["messages"])
        self.assertEqual(str(messages[0]), f"The object {self.user} has been not exported")
        self.assertTrue(mocked_folders.called)
        with self.assertRaisesMessage(ApiException, "No folders available"):
            self.client_api.get_folders(permission="write")
        mocked_folders.assert_called_with(
            url=url_list_folders,
            headers={
                "content-type": "application/json",
                "authorization": f"Token {self.config_object.api_key}",
            },
            params="write",
        )
