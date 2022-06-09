from django.test import TestCase
from django.urls import reverse

from .factories import StaffUserFactory, UserFactory


class TestExportMixinNotAuthUser(TestCase):
    """Not logged-in AND is_staff user is redirected to login page"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_export_mixin_render_login_template(self):
        """redirect to login; if login OK redirect to prev page"""
        resp = self.client.get(self.url, follow=True)
        next_url, status_code = resp.redirect_chain[-1]

        self.assertEqual(
            next_url, f"/admin/login/?next=/admin/auth/user/{self.user.id}/export/"
        )
        self.assertEqual(302, status_code)


class TestExportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected to login page"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_export", kwargs={"object_id": self.user.id})

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url, follow=True)

        self.assertEqual(
            resp.redirect_chain,
            [(f"/admin/login/?next=/admin/auth/user/{self.user.id}/export/", 302)],
        )


class TestImportMixinNotAuthStaffUser(TestCase):
    """Not logged-in AND is_staff user is redirected to loggin page"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url, follow=True)

        self.assertEqual(
            resp.redirect_chain, [("/admin/login/?next=/admin/auth/user/import/", 302)]
        )


class TestImportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected to loggin page;"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("admin:auth_user_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url, follow=True)

        self.assertEqual(
            resp.redirect_chain, [("/admin/login/?next=/admin/auth/user/import/", 302)]
        )
