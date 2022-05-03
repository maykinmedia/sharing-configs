from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import resolve, reverse

from .factories import StaffUserFactory

User = get_user_model()


class TestUrls(TestCase):
    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)

    def test_url_import_mixin(self):
        url = reverse("admin:auth_user_import")
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func.__name__, "import_from_view")

    def test_url_export_mixin(self):
        url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func.__name__, "sharing_configs_export_view")

    def test_url_import_ajax(self):
        url = reverse("admin:auth_user_ajax")
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func.__name__, "get_ajax_fetch_files")
