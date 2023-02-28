from django.core.management import BaseCommand

from wagtail_toolbox.wordpress.importer import Importer


class Command(BaseCommand):
    help = "Import WordPress data"

    def add_arguments(self, parser):
        parser.add_argument(
            "host",
            type=str,
            help="The host of the WordPress site.",
            default="",
        )
        parser.add_argument(
            "url",
            type=str,
            help="The url of the WordPress site json API.",
            default="",
        )
        # parser.add_argument(
        #     "endpoint",
        #     type=str,
        #     help="The API endpoint to fetch.",
        # )
        parser.add_argument(
            "model",
            type=str,
            help="The model to import data to.",
        )

    def handle(self, *args, **options):
        importer = Importer(
            host=options["host"],
            url=options["url"],
            # endpoint=options["endpoint"],
            model_name=options["model"],
        )
        importer.import_data()
