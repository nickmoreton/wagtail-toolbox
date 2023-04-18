from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from wagtail_toolbox.block_builder.html_parser import DomTagSignatureMaker
from wagtail_toolbox.wordpress.models.config import StreamBlockSignatureBlocks
from wagtail_toolbox.wordpress.models.wordpress import clean_html


class Command(BaseCommand):
    help = """Use this to inspect the possible html tag patterns in a wordpress content field.
    This will save the signatures to the database and allow you to map them to wagtail blocks.

    This will also output the signatures to the console.

    You can use the --signatures flag to only output the signatures.

    You can use the --dont-clean flag to not clean the content before inspecting.

    Signatures are either saved as new entries or updated if they already exist.

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

    def signatures_set(self, signatures):
        return set(signatures)

    def signatures_sorted(self, signatures):
        return sorted(signatures)

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

        results = apps.get_model(  # a queryset of all() WP records for the source-model
            options["source-model"],
        ).objects.all()
        self.stdout.write(self.style.WARNING(f"Inspecting {len(results)} results."))

        # generate signatures for all the results
        signatures = list()
        for result in results:
            if not options["dont_clean"]:
                result.content = clean_html(result.content)

            signature_maker = DomTagSignatureMaker(separator=":")
            signature_maker.feed(result.content)
            signatures.extend(signature_maker.get_signatures())

        signatures = set(signatures)

        if not options["signatures"]:
            # only save the signatures if we are not just outputting them
            for signature in signatures:
                block_name = default_block

                for k, v in default_mapping.items():
                    parts = signature.split(":")
                    if k in parts:
                        block_name = v
                        continue

                stream_block_signature = StreamBlockSignatureBlocks.objects.filter(
                    signature=signature
                )
                if stream_block_signature:
                    current_model = stream_block_signature[0].model.split(",")
                    if not options["source-model"] in current_model:
                        current_model.append(options["source-model"])
                    stream_block_signature[0].model = ",".join(current_model)
                    stream_block_signature[0].block_name = block_name
                    # stream_block_signature[0].block_kwargs = None
                    stream_block_signature[0].save()
                else:
                    stream_block_signature = StreamBlockSignatureBlocks.objects.create(
                        signature=signature,
                        model=options["source-model"],
                        block_name=default_block,
                        # block_kwargs=None,
                    )

        for signature in signatures:
            self.stdout.write(signature)

        self.stdout.write(self.style.SUCCESS(f"Found {len(signatures)} signatures."))
