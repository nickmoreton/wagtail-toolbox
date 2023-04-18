import sys

from bs4 import BeautifulSoup as bs4
from django.conf import settings
from django.utils.module_loading import import_string

# from wagtail_toolbox.block_builder.html_parser import DomTagSignatureMaker
from wagtail_toolbox.wordpress.models.config import StreamBlockSignatureBlocks


class WagtailBlockBuilder:
    def __init__(self, fallback_block_name=None, rich_text_block_name=None):
        if fallback_block_name is None and not hasattr(
            settings, "WPI_FALLBACK_BLOCK_NAME"
        ):
            self.fallback_block = (
                "wagtail_toolbox.wordpress.wagtail_builder_utils.raw_html"
            )
        else:
            self.fallback_block = settings.WPI_FALLBACK_BLOCK_NAME

        if rich_text_block_name is None and not hasattr(
            settings, "WPI_RICHTEXT_BLOCK_NAME"
        ):
            self.rich_text_block = (
                "wagtail_toolbox.wordpress.wagtail_builder_utils.rich_text"
            )
        else:
            self.rich_text_block = settings.WPI_RICHTEXT_BLOCK_NAME

        self.stream_blocks = []
        self.stream_block_signatures = StreamBlockSignatureBlocks.objects.all().values_list(
            "signature",
            "block_name",
            # "block_kwargs"
        )

    @staticmethod
    def make_tag_signature(element):
        """Make a signature for a BS4 tag and its children."""
        signature = f"{element.name}:"
        current = element.find()
        while current:
            signature += f"{current.name}:"
            current = current.find() if current.find() else None
        return signature

    def build(self, html):
        soup = bs4(html, "html.parser")
        block_stack = []

        for element in soup.findChildren(recursive=False):
            # TODO: use the new signature maker
            signature = self.make_tag_signature(element)

            try:
                stream_block_config = self.stream_block_signatures.get(
                    signature=signature
                )
            except StreamBlockSignatureBlocks.DoesNotExist:
                sys.stderr.write(f"Signature not found: {signature}\n")
                continue

            is_richtext = stream_block_config[1] == self.rich_text_block

            block_builder = import_string(stream_block_config[1])
            block = block_builder(str(element), signature=signature)

            if not block:  # deal with null blocks
                continue

            block_stack.append(block)  # add everything to the block stack

            # now fix up rich_text blocks as they should be one block
            # and not consecutive blocks
            if is_richtext and len(block_stack) > 1:
                # are the last 2 blocks on the stack a type="rich_text" block?
                # we know the last one is because of is_richtext
                if block_stack[-2]["type"] == "rich_text":
                    # pop the last block and get it's value
                    last_block_value = block_stack.pop()["value"]
                    # add the last_block_value to the last_block
                    block_stack[-1]["value"] += last_block_value

        return block_stack


make_tag_signature = WagtailBlockBuilder.make_tag_signature  # for convenience
