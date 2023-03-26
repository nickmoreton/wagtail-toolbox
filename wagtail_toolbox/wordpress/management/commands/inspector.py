import json

from bs4 import BeautifulSoup as bs4
from django.apps import apps
from django.core.management.base import BaseCommand

from wagtail_toolbox.wordpress.clean_html import HTMLCleaner


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
            "--clean",
            action="store_false",
            help="Clean the content before inspecting.",
        )

    def make_tag_signature(soup):
        """Make a signature for a BS4 tag and its children."""
        signature = f"{soup.name}:"
        current = soup.find()
        while current:
            signature += f"{current.name}:"
            current = current.find() if current.find() else current.find_next_sibling()
        return bs4(signature, "html.parser")

    def handle(self, *args, **options):
        wordpress_model = apps.get_model(options["source-model"])

        signatures = list()

        results = wordpress_model.objects.all()

        self.stdout.write(self.style.WARNING(f"Inspecting {len(results)} results."))

        for result in results:
            if options["clean"]:
                cleaner = HTMLCleaner(result.content)
                result.content = cleaner.clean_html()

            soup = bs4(result.content, "html.parser")

            for tag in soup.findChildren(recursive=False):
                signature = f"{tag.name}:"
                current = tag.find()

                while current and current.findChildren(recursive=False):
                    signature += f"{current.name}:"
                    current = current.find()

                signatures.append(signature)

        signatures = set(signatures)
        sorted_signatures = sorted(signatures)

        if options["signatures"]:
            for signature in sorted_signatures:
                self.stdout.write(signature)
            return

        settings = {}

        if hasattr(settings, "WPI_BLOCK_ACTIONS"):
            block_actions = settings.WPI_BLOCK_ACTIONS
        else:
            block_actions = {
                "address:": {"name": "address_block_builder", "kwargs": {}},
                "blockquote:": {"name": "blockquote_block_builder", "kwargs": {}},
                # "dl:": {"name": "dl_block_builder", "kwargs": {}},
                "figure:": {"name": "figure_block_builder", "kwargs": {}},
                "h1:": {"name": "title_block_builder", "kwargs": {"level": 1}},
                # "h2:": {"name": "title_block_builder", "kwargs": {"level": 2}},
                # "h3:": {"name": "title_block_builder", "kwargs": {"level": 3}},
                # "h4:": {"name": "title_block_builder", "kwargs": {"level": 4}},
                # "h5:": {"name": "title_block_builder", "kwargs": {"level": 5}},
                # "h6:": {"name": "title_block_builder", "kwargs": {"level": 6}},
                # "hr:": {"name": "hr_block_builder", "kwargs": {}},
                # "img:": {"name": "figure_block_builder", "kwargs": {}},
                # "ol:": {"name": "richtext_block_builder", "kwargs": {}},
                # "p:": {"name": "richtext_block_builder", "kwargs": {}},
                "pre:": {"name": "pre_block_builder", "kwargs": {}},
                "table:": {"name": "table_block_builder", "kwargs": {}},
                # "ul:": {"name": "richtext_block_builder", "kwargs": {}},
                "form:": {"name": "form_block_builder", "kwargs": {}},
                "iframe:": {"name": "embed_block_builder", "kwargs": {}},
            }

        for signature in sorted_signatures:
            if signature in block_actions:
                settings[signature] = {"builder": block_actions[signature]}
            else:
                settings[signature] = {"builder": {"name": "richtext_block_builder"}}
        self.stdout.write(
            f"Suggested settings for\nWPI_BLOCK_PATTERNS = {json.dumps(settings, indent=4)}"
        )
