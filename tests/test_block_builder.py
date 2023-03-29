from bs4 import BeautifulSoup as bs4
from django.test import TestCase, override_settings

from wagtail_toolbox.wordpress.block_builder import WagtailBlockBuilder


class WagtailBlockBuilderTest(TestCase):
    def setUp(self):
        self.builder = WagtailBlockBuilder()

    def test_fallback_block(self):
        builder = WagtailBlockBuilder()
        fallback_block = builder.fallback_block
        self.assertEqual(
            fallback_block,
            "wagtail_toolbox.wordpress.wagtail_builder_utils.raw_html_block_builder",
        )

    @override_settings(WPI_FALLBACK_BLOCK_NAME="invalid_block")
    def test_fallback_block_custom(self):
        builder = WagtailBlockBuilder()
        fallback_block = builder.fallback_block
        self.assertEqual(fallback_block, "invalid_block")

    def test_rich_text_block(self):
        builder = WagtailBlockBuilder()
        rich_text_block = builder.rich_text_block
        self.assertEqual(
            rich_text_block,
            "wagtail_toolbox.wordpress.wagtail_builder_utils.richtext_block_builder",
        )

    @override_settings(WPI_RICHTEXT_BLOCK_NAME="invalid_block")
    def test_rich_text_block_custom(self):
        builder = WagtailBlockBuilder()
        rich_text_block = builder.rich_text_block
        self.assertEqual(rich_text_block, "invalid_block")

    def test_make_tag_signature(self):
        element = "<p><strong>test</strong></p>"
        soup = bs4(element, "html.parser")
        tag_signature = self.builder.make_tag_signature(soup.find())
        self.assertEqual(tag_signature, "p:strong:")
