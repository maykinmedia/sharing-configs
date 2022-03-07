from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from .forms import ExportToForm, ImportForm
from .models import GithubConfig


@admin.register(GithubConfig)
class GithubConfigAdmin(SingletonModelAdmin):
    pass


class SharingConfigsExportMixin:
    def get_sharing_configs_export_data(self, obj, **form_kwargs):
        raise NotImplemented

    def sharing_configs_export_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj.name}.json"}
        if request.method == "POST":
            form = ExportToForm(
                request.POST,
                instance=obj,
                initial=initial,
                export_func=self.get_sharing_configs_export_data,
            )
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
            form = ExportToForm(initial=initial, instance=obj)

        return render(
            request,
            "admin/core/objecttype/export_to_github.html",
            {"object": obj, "form": form},
        )


class SharingConfigsImportMixin:
    pass
