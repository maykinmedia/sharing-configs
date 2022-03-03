from django.core.management.base import BaseCommand

from testapp import utils


class Command(BaseCommand):
    help = "List installed apps in settings.py"

    def handle(self, *args, **options):
        apps = utils.export_apps()
        str_apps = "\n".join([f"-{app}" for app in apps])
        pritty_print_apps = f"Successfully listed apps: {str_apps}"
        self.stdout.write(self.style.SUCCESS(pritty_print_apps))
