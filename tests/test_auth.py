from django.test import TestCase
from django.urls import reverse

from testapp.models import Configuration, Theme

from .factories import StaffUserFactory, ThemeFactory, UserFactory


class TestExportMixinNotAuthUser(TestCase):
    """Not logged-in AND is_staff user is redirected to login page"""

    def setUp(self) -> None:
        self.theme = ThemeFactory()
        self.configuration = Configuration.objects.create(theme=self.theme)
        self.url = reverse(
            "admin:testapp_theme_export", kwargs={"object_id": self.theme.id}
        )

    def test_export_mixin_render_login_template(self):
        """redirect to login; if login OK redirect to prev page"""
        resp = self.client.get(self.url, follow=True)
        next_url, status_code = resp.redirect_chain[-1]

        self.assertEqual(
            next_url, f"/admin/login/?next=/admin/testapp/theme/{self.theme.id}/export/"
        )
        self.assertEqual(302, status_code)


class TestExportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected to login page"""

    def setUp(self) -> None:
        self.theme = ThemeFactory()
        self.configuration = Configuration.objects.create(theme=self.theme)
        self.user = UserFactory()
        self.url = reverse(
            "admin:testapp_theme_export", kwargs={"object_id": self.theme.id}
        )
        self.client.force_login(self.user)

    def test_get_request_export_mixin(self):
        resp = self.client.get(self.url, follow=True)

        self.assertEqual(
            resp.redirect_chain,
            [(f"/admin/login/?next=/admin/testapp/theme/{self.theme.id}/export/", 302)],
        )


class TestImportMixinNotAuthStaffUser(TestCase):
    """Not logged-in AND is_staff user is redirected to loggin page"""

    def setUp(self) -> None:
        self.user = StaffUserFactory()
        self.theme = ThemeFactory()
        self.configuration = Configuration.objects.create(theme=self.theme)
        self.url = reverse("admin:testapp_theme_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url, follow=True)

        self.assertEqual(
            resp.redirect_chain,
            [("/admin/login/?next=/admin/testapp/theme/import/", 302)],
        )


class TestImportMixinAuthUserNotStaff(TestCase):
    """Logged-in user but NOT is_staff is redirected to loggin page;"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.theme = ThemeFactory()
        self.configuration = Configuration.objects.create(theme=self.theme)
        self.client.force_login(self.user)
        self.url = reverse("admin:testapp_theme_import")

    def test_get_request_import_mixin(self):
        resp = self.client.get(self.url, follow=True)

        self.assertEqual(
            resp.redirect_chain,
            [("/admin/login/?next=/admin/testapp/theme/import/", 302)],
        )
