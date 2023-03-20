from bs4 import BeautifulSoup as bs
from django.test import TestCase, override_settings

from wagtail_toolbox.wordpress.content_cleaner import ContentCleaner

from .config import TestConfig

test_config = TestConfig()


@override_settings(
    WPI_BLOCK_PATTERNS=test_config.block_patterns,
    WPI_RICHTEXT_PATTERNS=test_config.richtext_patterns,
)
class TestCleaner(TestCase):
    def setUp(self):
        super().setUp()
        with open("tests/fixtures/test.html") as f:
            self.content = f.read()
        self.expected_text = "This should be left in place without any changes"

    def test_patterns_allowed(self):
        cleaner = ContentCleaner(self.content)
        soup = bs(cleaner.clean(), "html.parser")
        # print(soup)
        paragraph = soup.find("p")
        self.assertTrue(paragraph)
        self.assertTrue(paragraph.text == self.expected_text)

        heading_2 = soup.find("h2")
        self.assertTrue(heading_2)
        self.assertTrue(heading_2.text == self.expected_text)

        heading_3 = soup.find("h3")
        self.assertTrue(heading_3)
        self.assertTrue(heading_3.text == self.expected_text)

        heading_4 = soup.find("h4")
        self.assertTrue(heading_4)
        self.assertTrue(heading_4.text == self.expected_text)

        heading_5 = soup.find("h5")
        self.assertTrue(heading_5)
        self.assertTrue(heading_5.text == self.expected_text)

        heading_6 = soup.find("h6")
        self.assertTrue(heading_6)
        self.assertTrue(heading_6.text == self.expected_text)

        unordered_list = soup.find("ul")
        self.assertTrue(unordered_list)
        unordered_list_item = unordered_list.find("li")
        self.assertTrue(unordered_list_item.text == self.expected_text)

        ordered_list = soup.find("ol")
        self.assertTrue(ordered_list)
        ordered_list_item = ordered_list.find("li")
        self.assertTrue(ordered_list_item.text == self.expected_text)

        imgage = soup.find("img")
        self.assertTrue(imgage)

        anchor = soup.find("a")
        self.assertTrue(anchor)
        self.assertTrue(anchor.text == self.expected_text)

        superscript = soup.find("sup")
        self.assertTrue(superscript)
        self.assertTrue(superscript.text == self.expected_text)

        subscript = soup.find("sub")
        self.assertTrue(subscript)
        self.assertTrue(subscript.text == self.expected_text)

        bold = soup.find("strong")
        self.assertTrue(bold)
        self.assertTrue(bold.text == self.expected_text)

        italic = soup.find("em")
        self.assertTrue(italic)
        self.assertTrue(italic.text == self.expected_text)

        strikethough = soup.find("del")
        self.assertTrue(strikethough)
        self.assertTrue(strikethough.text == self.expected_text)

        preformatted_code = soup.find("code")
        self.assertFalse(preformatted_code)  # TODO test for a block

        horizontal_rule = soup.find("hr")
        self.assertTrue(horizontal_rule)

    def test_patterns_removed(self):
        cleaner = ContentCleaner(self.content)
        soup = bs(cleaner.clean(), "html.parser")
        # divs with text content should become paragraphs
        self.assertFalse(soup.find("div"))
        self.assertFalse(soup.find("span"))
