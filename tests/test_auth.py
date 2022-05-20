from django.test import TestCase
from django.urls import reverse

from .factories import StaffUserFactory, UserFactory


class TestExportMixinNotAuthUser(TestCase):
    """Not logged-in AND is_staff user is redirected to login page"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_export_mixin_redirect(self):
        """re-direct"""
        resp = self.client.get(self.url)
        self.assertEqual(302, resp.status_code)

    def test_export_mixin_render_login_template(self):
        """render loggin template; redirect back if loggin OK"""
        resp = self.client.get(self.url, follow=True)
        next_url, status_code = resp.redirect_chain[-1]
        self.assertEqual(
            next_url, f"/admin/login/?next=/admin/auth/user/{self.user.id}/export/"
        )
        self.assertEqual(302, status_code)
        self.assertTemplateUsed(resp, "admin/login.html")


class TestExportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected to login page"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(resp, "admin/login.html")


class TestImportMixinNotAuthStaffUser(TestCase):
    """Not logged-in AND is_staff user is redirected to loggin page"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(resp, "admin/login.html")


class TestImportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected to loggin page"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(resp, "admin/login.html")
