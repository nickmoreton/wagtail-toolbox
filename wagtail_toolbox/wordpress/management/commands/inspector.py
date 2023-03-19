from bs4 import BeautifulSoup
from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Use this to inspect the possible html tag patterns in a wordpress content field.
    This will output a list of patterns that can be used in the block_patterns dict in the
    content_cleaner.py file."""

    def add_arguments(self, parser):
        parser.add_argument(
            "source-model",
            type=str,
            help="The wordpress model to transfer. e.g. wordpress.WPPost",
        )

    def handle(self, *args, **options):
        wordpress_model = apps.get_model(options["source-model"])
        block_patterns = []
        allow_top_level_patterns = [
            # These patterns should be fine in a rich text field
            "p:",
            "h2:",
            "h3:",
            "h4:",
            "h5:",
            "h6:",
            "ul:",
            "ol:",
            "img:",
            "a:",
            "sup:",
            "sub:",
            "strong:",
            "em:",
            "strike:",
            "code:",
            "hr:",
        ]

        for result in wordpress_model.objects.all():
            soup = BeautifulSoup(result.content, "html.parser")
            for tag in soup.findChildren(recursive=False):
                tag_pattern = f"{tag.name}:"
                if tag_pattern in allow_top_level_patterns:
                    continue
                current = tag.find()

                while current:
                    tag_pattern += f"{current.name}:"
                    current = current.find()

                block_patterns.append(tag_pattern)

        self.tag_set = sorted(set(block_patterns))

        self.out_as_list(self.tag_set)

    def out_as_list(self, list):
        for item in list:
            self.stdout.write(item)
