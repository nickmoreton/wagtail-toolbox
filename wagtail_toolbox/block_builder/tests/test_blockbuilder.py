from django.test import SimpleTestCase

from wagtail_toolbox.block_builder.html_parser import DomTagSignatureMaker


class DomTagSignatureMakerTest(SimpleTestCase):
    def test_get_signature(self):
        maker = DomTagSignatureMaker()
        maker.feed(
            """
        <div>
            <p>
                <a href="#">Link</a></p></div>
        """
        )
        result = maker.get_signatures()
        self.assertIn("div>p>a>", result)

    def test_get_signature_duplicate(self):
        maker = DomTagSignatureMaker()
        maker.feed(
            """
        <div>
            <p>
                <a href="#">Link</a></p></div>
        <div>
            <p>
                <a href="#">Link</a></p></div>
        """
        )
        result = maker.get_signatures()
        self.assertIn("div>p>a>", result)

    def test_get_signature_unique(self):
        maker = DomTagSignatureMaker()
        maker.feed(
            """
        <div>
            <p>
                <a href="#">Link</a></p></div>
        <ul>
            <li>
                <a href="#">Link</a></li></ul>
        """
        )
        result = maker.get_signatures()
        self.assertIn("div>p>a>", result)
        self.assertIn("ul>li>a>", result)

    def test_get_signature_duplicate_unique(self):
        maker = DomTagSignatureMaker()
        maker.feed(
            """
        <div>
            <p>
                <a href="#">Link</a></p></div>
        <div>
            <p>
                <a href="#">Link</a></p></div>
        <ul>
            <li>
                <a href="#">Link</a></li></ul>
        """
        )
        result = maker.get_signatures()
        self.assertIn("div>p>a>", result)
        self.assertIn("ul>li>a>", result)

    def test_get_signature_one(self):
        maker = DomTagSignatureMaker()
        maker.feed(
            """
        <div></div>
        """
        )
        result = maker.get_signatures()
        self.assertIn("div>", result)

    def test_separator(self):
        maker = DomTagSignatureMaker(separator=":")
        maker.feed(
            """
        <div>
            <p>
                <a href="#">Link</a></p></div>
        """
        )
        result = maker.get_signatures()
        self.assertIn("div:p:a:", result)

    def test_attrs(self):
        maker = DomTagSignatureMaker(include_attrs=True)
        maker.feed(
            """
        <div class="anchor" id="anchor-1">
            <p>
                <a href="http://example.com" class="link">Link</a></p></div>
        """
        )
        result = maker.get_signatures()
        self.assertIn(
            "div[class=anchor,id=anchor-1]>p>a[class=link,href=http://example.com]>",
            result,
        )

    def test_feed_first(self):
        maker = DomTagSignatureMaker()
        maker.feed(
            """
        <div>
            <p>
                <a href="#">Link</a></p></div>
        <ul>
            <li>
                <a href="#">Link</a></li></ul>
        """
        )
        result = maker.get_signatures(first_only=True)
        self.assertIn("div>p>a>", result)
        self.assertNotIn("ul>li>a>", result)
