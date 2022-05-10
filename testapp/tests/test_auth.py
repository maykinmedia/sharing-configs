from django.test import Client, TestCase
from django.urls import reverse

from .factories import StaffUserFactory, UserFactory


class TestExportMixinNotAuthUser(TestCase):
    """Not logged-in AND is_staff user is redirected to login page"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)


class TestExportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected to login page"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)


class TestImportMixinNotAuthStaffUser(TestCase):
    """Not logged-in AND is_staff user is redirected"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)


class TestImportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)
