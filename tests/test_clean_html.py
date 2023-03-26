from django.test import TestCase

from wagtail_toolbox.wordpress.clean_html import HTMLCleaner


class TestCleanHtmlClass(TestCase):
    def setUp(self):
        from pathlib import Path

        cwd = Path.cwd()
        fixtures_dir = cwd / "tests" / "fixtures"
        with open(fixtures_dir / "test_cleaner.html", "r") as f:
            self.html_data = f.read()

        self.html_parser = HTMLCleaner()

    def test_no_clean_tags(self):
        self.output = self.html_parser.clean_html(self.html_data)
        # print(self.output)

        self.assertTrue("<div>" not in self.output)
        self.assertTrue(
            "<p>This page tests how the theme displays the columns block."
            in self.output
        )
        self.assertTrue(
            "<p>This is the second column block. It has <strong>3</strong> columns.</p>"
            in self.output
        )
        self.assertTrue(
            "<p>To change the number of columns, select the column block to open the settings panel."
            in self.output
        )
        self.assertTrue(
            """<figure class="wp-block-media-text__media">""" in self.output
        )

    def test_clean_tags(self):
        self.output = self.html_parser.clean_html(
            self.html_data, clean_tags=["p", "div", "figure"]
        )
        self.assertTrue("<p>" not in self.output)
        self.assertTrue("<div>" not in self.output)
        self.assertTrue("<figure>" not in self.output)

        self.output = self.html_parser.clean_html(
            self.html_data, clean_tags=["p", "figure", "strong"]
        )
        self.assertTrue("<p>" not in self.output)
        self.assertTrue("<strong>" not in self.output)
        self.assertTrue("<figure>" not in self.output)
        self.assertTrue("div" in self.output)

    def test_no_html_data(self):
        self.output = self.html_parser.clean_html()
        self.assertTrue(self.output is None)

    # # some quick tests
    # assert "<p>This page tests how the theme displays the columns block." in output
    # assert (
    #     "<p>This is the second column block. It has <strong>3</strong> columns.</p>"
    #     in output
    # )
    # assert (
    #     "<p>To change the number of columns, select the column block to open the settings panel."
    #     in output
    # )
    # assert """<figure class="wp-block-media-text__media">""" in output

    # html_parser = HTMLCleaner(html_data, clean_tags=["p", "div", "figure"])
    # output = html_parser.clean_html()

    # # some quick tests
    # assert "<p>" not in output
    # assert "<div>" not in output
    # assert "<figure>" not in output

    # html_parser = HTMLCleaner(html_data, clean_tags=["p", "figure", "strong"])
    # output = html_parser.clean_html()

    # # some quick tests
    # assert "<p>" not in output
    # assert "<strong>" not in output
    # assert "<figure>" not in output
    # assert "div" in output
