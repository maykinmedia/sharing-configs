from django.core.management.base import BaseCommand, CommandError
from testapp import utils

class Command(BaseCommand):
    help = 'List installed apps in settings.py'
    
    def handle(self, *args, **options):
        apps = utils.export_apps()
        print('installed_apps',apps)
        self.stdout.write(self.style.SUCCESS('Successfully listed apps:'))