from fileinput import filename
from unittest import mock
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import requests

from ..client_util import SharingConfigsClient
from ..models import SharingConfigsConfig
from .factories import StaffUserFactory

User = get_user_model()


class TestImportMixin(TestCase):
    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)

    def test_import_valid_form(self):
        """redirect on success if import form valid"""
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": "zoo.txt"}
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)

    def test_fail_import_form_without_file(self):
        """if file name not in data, form with error message rendered in a template"""
        url = reverse("admin:auth_user_import")
        data = {"folder": "folder_one", "file_name": ""}
        resp = self.client.post(url, data=data)
        form = resp.context["form"]
        file_field = resp.context["form"].fields["file_name"]
        err_msg = file_field.error_messages.get("required", None)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(form.is_bound, True)
        self.assertEqual(file_field.required, True)
        self.assertEqual(err_msg, "This field is required.")
