from bs4 import BeautifulSoup as bs4
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from wagtail_toolbox.wordpress.models.config import StreamBlockSignatureBlocks
from wagtail_toolbox.wordpress.models.wordpress import clean_html
from wagtail_toolbox.wordpress.wagtail_block_builder import make_tag_signature


class Command(BaseCommand):
    help = """Use this to inspect the possible html tag patterns in a wordpress content field.
    This will save the signatures to the database and allow you to map them to wagtail blocks.

    This will also output the signatures to the console.

    You can use the --signatures flag to only output the signatures.

    You can use the --dont-clean flag to not clean the content before inspecting.

    Example:
        Console only output:
            python manage.py inspector wordpress.WPPost --signatures

        Save signatures to database:
            python manage.py inspector wordpress.WPPost
    """

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
        else:
            default_mapping = {}

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

                if not options["signatures"]:
                    stream_block_signature = StreamBlockSignatureBlocks.objects.filter(
                        signature=signature
                    )

                    if stream_block_signature:
                        current_model = stream_block_signature[0].model.split(",")
                        if not options["source-model"] in current_model:
                            current_model.append(options["source-model"])
                        stream_block_signature[0].model = ",".join(current_model)
                        stream_block_signature[0].block_name = block_name
                        stream_block_signature[0].block_kwargs = None
                        stream_block_signature[0].save()
                    else:
                        stream_block_signature = (
                            StreamBlockSignatureBlocks.objects.create(
                                signature=signature,
                                model=options["source-model"],
                                block_name=block_name,
                                block_kwargs=None,
                            )
                        )

        signatures = set(signatures)
        sorted_signatures = sorted(signatures)
        for signature in sorted_signatures:
            self.stdout.write(signature)

        self.stdout.write(self.style.SUCCESS(f"Found {len(signatures)} signatures."))
