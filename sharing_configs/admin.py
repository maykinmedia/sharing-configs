from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from .forms import ExportToGithubForm, GithubImportForm
from .models import SharingConfigsConfig


@admin.register(SharingConfigsConfig)
class SharingConfigsConfigAdmin(SingletonModelAdmin):
    pass


class GitHubExportImportMixin:
    def get_urls(self):
        urls = super().get_urls()

        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path(
                "import-from-github/",
                self.admin_site.admin_view(self.import_from_github_view),
                name="import_from_github",
            ),
            path(
                "<path:object_id>/export-to-github/",
                self.admin_site.admin_view(self.export_to_github_view),
                name="%s_%s_export_to_github" % info,
            ),
        ]
        return my_urls + urls

    def import_from_github_view(self, request):
        if request.method == "POST":
            form = GithubImportForm(request.POST)
            if form.is_valid():
                object_type = form.save()
                msg = format_html(
                    _("The object type {object_type} has been imported successfully!"),
                    object_type=object_type,
                )
                self.message_user(request, msg, level=messages.SUCCESS)
                return redirect(reverse("admin:core_objecttype_changelist"))
        else:
            form = GithubImportForm()

        return render(
            request, "admin/core/objecttype/import_from_github.html", {"form": form}
        )

    def export_to_github_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj.name}.json"}

        if request.method == "POST":
            form = ExportToGithubForm(request.POST, instance=obj, initial=initial)
            if form.is_valid():
                commit = form.save()
                msg = format_html(
                    _(
                        "The object type {object_type} has been exported successfully in the {commit} commit"
                    ),
                    object_type=obj,
                    commit=commit.sha,
                )
                self.message_user(request, msg, level=messages.SUCCESS)

        else:
            form = ExportToGithubForm(initial=initial, instance=obj)

        return render(
            request,
            "admin/core/objecttype/export_to_github.html",
            {"object": obj, "form": form},
        )
