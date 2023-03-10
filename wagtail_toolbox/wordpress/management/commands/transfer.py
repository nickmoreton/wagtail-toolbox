from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Transport WordPress posts to Wagtail
        Usage: python manage.py transport <source_model> <target_model> <wordpress_ids>
        Example: python manage.py transport WPPost BlogPage 1,2,3
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "source_model",
            type=str,
            help="The wordpress model to transfer.",
        )
        parser.add_argument(
            "target_model",
            type=str,
            help="The wagtail model to transfer to.",
        )
        parser.add_argument(
            "primary_keys",
            type=str,
            help="The primary keys of the wordpress models to transfer.",
        )

    def handle(self, *args, **options):
        source_model = apps.get_model(options["source_model"])
        primary_keys = options["primary_keys"].split(",")

        source_queryset = source_model.objects.filter(pk__in=primary_keys)

        transfer_action = source_model.transfer_data(source_model, source_queryset)

        if transfer_action:
            self.stdout.write(f"{transfer_action['model']} transferred successfully.")
            self.stdout.write(
                f"Created: {transfer_action['created']} Updated: {transfer_action['updated']}"
            )
            self.stdout.write(self.style.SUCCESS("Data transfer successful"))
        else:
            self.stdout.write(self.style.ERROR("Data transfer failed"))
