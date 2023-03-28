from bs4 import BeautifulSoup as bs4
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from wagtail_toolbox.wordpress.models.config import StreamBlockSignatureBlocks
from wagtail_toolbox.wordpress.models.wordpress import clean_html
from wagtail_toolbox.wordpress.wagtail_block_builder import make_tag_signature


class Command(BaseCommand):
    help = """Use this to inspect the possible html tag patterns in a wordpress content field.
    This will output a list of patterns that can be used in the block_patterns dict for building
    streamfield content."""

    def add_arguments(self, parser):
        parser.add_argument(
            "source-model",
            type=str,
            help="The wordpress model to transfer. e.g. wordpress.WPPost",
        )
        parser.add_argument(
            "--signatures",
            action="store_true",
            help="Only output the signature patterns.",
        )
        parser.add_argument(
            "--dont-clean",
            action="store_true",
            help="Clean the content before inspecting.",
        )

    def handle(self, *args, **options):
        if hasattr(settings, "WPI_STREAM_BLOCK_DEFAULT"):
            default_block = settings.WPI_STREAM_BLOCK_DEFAULT
        else:
            default_block = (
                "wagtail_toolbox.wordpress.wagtail_builder_utils.richtext_block_builder"
            )

        if hasattr(settings, "WPI_INSPECTOR_DEFAULT_MAPPING"):
            default_mapping = settings.WPI_INSPECTOR_DEFAULT_MAPPING

        wordpress_model = apps.get_model(options["source-model"])

        signatures = list()

        results = wordpress_model.objects.all()

        self.stdout.write(self.style.WARNING(f"Inspecting {len(results)} results."))

        for result in results:
            if not options["dont_clean"]:
                result.content = clean_html(result.content)

            soup = bs4(result.content, "html.parser")

            for tag in soup.findChildren(recursive=False):
                signature = make_tag_signature(tag)

                signatures.append(signature)

                block_name = default_block

                for k, v in default_mapping.items():
                    parts = signature.split(":")
                    if k in parts:
                        block_name = v
                        continue

                obj, updated = StreamBlockSignatureBlocks.objects.update_or_create(
                    signature=signature,
                    defaults={
                        "block_name": block_name,
                        "block_kwargs": None,
                    },
                )

        signatures = set(signatures)
        sorted_signatures = sorted(signatures)
        for signature in sorted_signatures:
            self.stdout.write(signature)

        self.stdout.write(self.style.SUCCESS(f"Found {len(signatures)} signatures."))
