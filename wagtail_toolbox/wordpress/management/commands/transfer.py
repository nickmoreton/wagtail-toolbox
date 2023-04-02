from django.conf import settings
from django.core.management.base import BaseCommand

from wagtail_toolbox.wordpress.wagtail_transfer import Transferrer


class Command(BaseCommand):
    help = """Transfer data from a wordpress model to a wagtail model."""

    def add_arguments(self, parser):
        parser.add_argument(
            "source-model",
            type=str,
            help="The wordpress model to transfer. e.g. wordpress.WPPost",
        )
        parser.add_argument(
            "target-model",
            type=str,
            help="The wagtail model to transfer to. e.g. blog.BlogPage",
        )
        parser.add_argument(
            "primary-keys",
            type=str,
            help="The primary keys of the wordpress models to transfer. Comma separated pk's e.g. 1,2,3",
        )
        parser.add_argument(
            "--clean-tags",
            type=str,
            help="The tags to remove from the html. Comma separated tags e.g. p,div",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the command without actually transferring data.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Transfer all data from the source model.",
        )

    def handle(self, *args, **options):
        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    "Running in dry-run mode, no data will be transferred."
                )
            )

        if hasattr(settings, "WPI_CLEAN_TAGS") and settings.WPI_CLEAN_TAGS:
            self.clean_tags = settings.WPI_CLEAN_TAGS

        if options["clean_tags"]:
            self.clean_tags = options["clean_tags"]

        if self.clean_tags and options["clean_tags"]:
            self.stdout.write(
                self.style.WARNING(
                    "Both WPI_CLEAN_TAGS and --clean-tags have been set. --clean-tags will take precedence."
                )
            )

        transferrer = Transferrer(
            wordpress_source=options["source-model"],
            wagtail_target=options["target-model"],
            wordpress_primary_keys=options["primary-keys"],
            dry_run=options["dry_run"],
            all=options["all"],
            clean_tags=self.clean_tags,
        )

        result = transferrer.transfer()

        if not result:
            self.stdout.write(self.style.ERROR("No data to transfer"))
            return

        self.complete(result)

    def complete(self, result):
        for key, value in result.items():
            self.stdout.write(f"{key}: {value}")

        self.stdout.write(self.style.SUCCESS("Successfully transferred data"))
