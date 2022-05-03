from django.conf import settings


def export_apps() -> list:
    """
    Check if settings is installed and return the current list
    of installed apps
    """
    list_installed_apps = getattr(settings, "INSTALLED_APPS", "No settings")
    return list_installed_apps
