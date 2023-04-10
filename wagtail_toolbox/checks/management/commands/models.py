from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # A counter that counts to 10000 and outputs the numbers

    def handle(self, *args, **options):
        for app in apps.get_app_configs():
            self.stdout.write(f"Models for {app.label}:")
            for model in app.get_models():
                self.stdout.write(f"- {model.__name__}")
