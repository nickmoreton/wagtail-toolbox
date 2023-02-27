from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--model",
            dest="model",
            default="all",
            help="The model to import from the Wordpress site",
        )

    def handle(self, *args, **options):
        self.stdout.write("Hello World")
