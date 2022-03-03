from django.conf import settings

def export_apps():
    list_installed_apps = getattr(settings,'INSTALLED_APPS')
    return list_installed_apps

