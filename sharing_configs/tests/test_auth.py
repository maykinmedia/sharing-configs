from django.test import Client, TestCase
from django.urls import reverse

from .factories import StaffUserFactory, UserFactory


class TestExportMixinAccess(TestCase):
    """logged-in AND is_staff user can get access to the template export mixin"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        """Tests that a GET request works and renders the correct
        template"""
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "sharing_configs/admin/export.html")


class TestExportMixinNotAuthUser(TestCase):
    """Tests that a not logged-in AND is_staff user is redirected"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)


class TestExportMixinAuthUserNotStaff(TestCase):
    """Tests that a logged-in user but NOT is_staff is redirected"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)


class TestImportMixinAccess(TestCase):
    """logged-in AND is_staff user can get access to the template import mixin"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        """Tests that a GET request works and renders the correct
        template"""
        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "sharing_configs/admin/import.html")


class TestImportMixinNotAuthStaffUser(TestCase):
    """Tests that a not logged-in AND is_staff user is redirected"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)


class TestImportMixinAuthUserNotStaff(TestCase):
    """Tests that a logged-in user but NOT is_staff is redirected"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
