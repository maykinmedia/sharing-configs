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
    """
    A class that prepares data and privides interface to make API request using credentials;
    The  get_sharing_configs_export_data() method raise NotImplementedError and should be
    overriden in a derived class.
    """

    change_form_template = "sharing_configs/admin/change_form.html"
    change_form_export_template = "sharing_configs/admin/export.html"

    def get_sharing_configs_export_data(self, obj: object) -> str:
        """
        Derived class should provide object to export
        """
        raise NotImplemented

    def sharing_configs_export_view(self, request, object_id):
        """
        return template with form for GET request;
        process form data in POST request and make API call to endpoint
        """
        obj = self.get_object(request, object_id)
        initial = {"file_name": f"{obj.username}.json"}
        # initial = {"file_name": f"{obj.name}.json"} # user obj has NO attr name
        if request.method == "POST":
            form = ExportToForm(request.POST, initial=initial)
            if form.is_valid():
                author = request.user
                obj_to_export = self.get_sharing_configs_export_data(obj)
                file_name = form.cleaned_data.get("file_name")
                folder_name = form.cleaned_data.get("folder_name")
                #  api call try/except request.post(url,data,headers)
                msg = format_html(
                    _(
                        "The object {object} has been exported successfully in the {result} result"
                    ),
                    object=obj,
                )
                self.message_user(request, msg, level=messages.SUCCESS)

        else:
            form = ExportToForm(initial=initial)

        return render(
            request,
            # self.change_form_template,
            self.change_form_export_template,
            {"object": obj, "form": form},
        )

    def get_urls(self):
        urls = super().get_urls()
        info = (
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        my_urls = [
            path(
                "<path:object_id>/export/",
                self.admin_site.admin_view(self.sharing_configs_export_view),
                name="%s_%s_export" % info,
            ),
        ]
        # my_urls == [<URLPattern '<path:object_id>/export-to/' [name='auth_user_export']>]
        return my_urls + urls


class SharingConfigsImportMixin:
    """provide methods to download files from storage using credentials"""

    import_template = "sharing_configs/admin/import.html"

    def get_sharing_configs_import_data(
        self, filename: str, folder: str, author: str
    ) -> object:
        """
        Derived class should override params to import an object;
        Also implement the way received object could be stored

        """
        raise NotImplemented

    def import_from_view(self, request):
        """
        return template with form and process data if form filled;
        make API call to API point to download object

        """
        if request.method == "POST":
            form = ImportForm(request.POST)
            if form.is_valid():
                object = form.save()
                # TODO: call to API to fetch object using form data
                msg = format_html(
                    _("The object {object} has been imported successfully!"),
                    object=object,
                )
                self.message_user(request, msg, level=messages.SUCCESS)
                return redirect(reverse("admin:import"))
        else:
            form = ImportForm()

            return render(request, self.import_template, {"form": form})

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-from/",
                self.admin_site.admin_view(self.import_from_view),
                name="import",
            ),
        ]
        # [<URLPattern 'import-from/' [name='import']>]
        return my_urls + urls
