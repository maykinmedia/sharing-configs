from django.test import Client, TestCase
from django.urls import reverse

from .factories import UserFactory,StaffUserFactory


class TestExportMixinAuthUser(TestCase):
    """logged-in AND is_staff user can get access to templates export mixin"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        """Tests that a GET request works and renders the correct
        template"""
        resp = self.client.get(self.url)
        # form = resp.context.__dict__   # {}
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "sharing_configs/admin/export.html")


class TestExportMixinNonAuthUser(TestCase):
    """Tests that a non-logged in staff user is redirected"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)


class TestExportMixinAuthUserNotStaff(TestCase):
    """Tests that a logged in user but NOT is_staff is redirected"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
