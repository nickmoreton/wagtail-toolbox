from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Purges all WordPress and/or Wagtail model objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            type=str,
            help="The model to purge.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Purge all models ",
        )
        parser.add_argument(
            "--dryrun",
            action="store_true",
            help="Dry run. Don't actually delete anything.",
        )

    def handle(self, *args, **options):
        confirm = input("Are you sure you want to purge all models? [y/N] ")
        if confirm.lower() != "y":
            return self.stdout.write(self.style.ERROR("Aborted."))

        if options["model"] and not options["all"]:
            try:
                model = apps.get_model("wordpress", options["model"])
            except LookupError:
                return self.stdout.write(self.style.ERROR("Model not found."))
            queryset = model.objects.all()

            if not queryset:
                self.stdout.write(self.style.SUCCESS("No objects to purge."))
                return

            for obj in queryset:
                if not options["dryrun"]:
                    obj.delete()
                self.stdout.write(f"Successfully purged {obj}")
            return self.stdout.write(self.style.SUCCESS("Done!"))

        if options["all"]:
            exclude_wordpress_models = ["WordpressSettings", "Endpoint"]
            for model in apps.get_app_config("wordpress").get_models():
                if model.__name__ in exclude_wordpress_models:
                    continue
                queryset = model.objects.all()

                if not queryset:
                    self.stdout.write(
                        self.style.WARNING(f"No objects to purge. {model.__name__}")
                    )
                    continue

                self.stdout.write(f"Purging {model.__name__}", ending="... ")
                for obj in queryset:
                    if not options["dryrun"]:
                        obj.delete()
                    self.stdout.write(f"{obj}, ", ending="")
                self.stdout.write(self.style.SUCCESS("\nDone!"))
            return

        return self.stdout.write(self.style.ERROR("No model or --all flag provided."))
