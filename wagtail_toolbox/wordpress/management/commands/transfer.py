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

        results, related, many_to_many = source_model.transfer_data(
            source_model, source_queryset
        )

        print(related)
        # for related_object in related:
        #     print(f'Setting {related_object["related_obj"]} related data on {related_object["target_obj"]}')
        #     related_model = apps.get_model(related_object["related_model"])
        #     fields = [
        #         field.name
        #         for field in related_model._meta.get_fields()
        #         if field.name in related_object["related_obj"]._meta.get_fields()
        #     ]
        #     print(fields)
        # obj, created = related_model.objects.get_or_create(
        #     **related_object["related_obj"]
        # )

        # for obj in many_to_many:
        #     print(f"Transferring {obj} many to many data")

        if results:
            self.stdout.write(f"{results['model']} transferred successfully.")
            self.stdout.write(
                f"Created: {results['created']} Updated: {results['updated']}"
            )
            self.stdout.write(self.style.SUCCESS("Data transfer successful"))
        else:
            self.stdout.write(self.style.ERROR("Data transfer failed"))
