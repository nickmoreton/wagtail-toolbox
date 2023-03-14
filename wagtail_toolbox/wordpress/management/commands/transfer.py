from django.core.management.base import BaseCommand

from wagtail_toolbox.wordpress.wagtail_transfer import Transferrer


class Command(BaseCommand):
    help = """Transport WordPress posts to Wagtail
        Usage: python manage.py transport <source_model> <target_model> <wordpress_ids>
        Example: python manage.py transport WPPost BlogPage 1,2,3
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "source-model",
            type=str,
            help="The wordpress model to transfer. Needs a dotter path to the model.",
        )
        parser.add_argument(
            "target-model",
            type=str,
            help="The wagtail model to transfer to. Needs a dotter path to the model.",
        )
        parser.add_argument(
            "primary-keys",
            type=str,
            help="The primary keys of the wordpress models to transfer. Comma separated pk's.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the command without actually transferring data.",
        )
        parser.add_argument(
            "--no-related",
            action="store_true",
            help="Do not transfer related data.",
        )

    def handle(self, *args, **options):
        transferrer = Transferrer(
            wordpress_source=options["source-model"],
            wagtail_target=options["target-model"],
            wordpress_primary_keys=options["primary-keys"],
        )

        result = transferrer.transfer()

        if not result:
            print("No data to transfer")
            return

        self.stdout.write(f"{result}")
        self.stdout.write(self.style.SUCCESS("Successfully transferred data"))
