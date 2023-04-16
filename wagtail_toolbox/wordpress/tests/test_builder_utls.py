from django.test import SimpleTestCase

from wagtail_toolbox.wordpress.wagtail_builder_utils import (
    block_quote,
    description,
    embed,
    heading,
)


class TestHeading(SimpleTestCase):
    def test_h1(self):
        html = "<h1>Heading</h1>"
        block = heading(html)
        self.assertEqual(block["type"], "heading")
        self.assertEqual(block["value"]["text"], "Heading")
        self.assertEqual(block["value"]["importance"], "h1")

    def test_h2(self):
        html = "<h2>Heading</h2>"
        block = heading(html)
        self.assertEqual(block["type"], "heading")
        self.assertEqual(block["value"]["text"], "Heading")
        self.assertEqual(block["value"]["importance"], "h2")

    def test_h3(self):
        html = "<h3>Heading</h3>"
        block = heading(html)
        self.assertEqual(block["type"], "heading")
        self.assertEqual(block["value"]["text"], "Heading")
        self.assertEqual(block["value"]["importance"], "h3")

    def test_h4(self):
        html = "<h4>Heading</h4>"
        block = heading(html)
        self.assertEqual(block["type"], "heading")
        self.assertEqual(block["value"]["text"], "Heading")
        self.assertEqual(block["value"]["importance"], "h4")

    def test_h5(self):
        html = "<h5>Heading</h5>"
        block = heading(html)
        self.assertEqual(block["type"], "heading")
        self.assertEqual(block["value"]["text"], "Heading")
        self.assertEqual(block["value"]["importance"], "h5")

    def test_h6(self):
        html = "<h6>Heading</h6>"
        block = heading(html)
        self.assertEqual(block["type"], "heading")
        self.assertEqual(block["value"]["text"], "Heading")
        self.assertEqual(block["value"]["importance"], "h6")

    def test_no_heading(self):
        html = "<p>Heading</p>"
        block = heading(html)
        self.assertIsNone(block)

    def test_no_text(self):
        html = "<h1></h1>"
        block = heading(html)
        self.assertEqual(block["type"], "heading")
        self.assertEqual(block["value"]["text"], "")
        self.assertEqual(block["value"]["importance"], "h1")


class TestBlockquote(SimpleTestCase):
    def test_blockquote_p(self):
        html = "<blockquote><p>Quote</p></blockquote>"
        kwargs = {
            "signature": "blockquote:p:",
        }
        block = block_quote(html, **kwargs)
        self.assertEqual(block["type"], "block_quote")
        self.assertEqual(block["value"]["quote"], "<p>Quote</p>")
        self.assertEqual(block["value"]["attribution"], "")

    def test_blockquote_cite(self):
        html = "<blockquote><p>Quote</p><cite>Attribution</cite></blockquote>"
        kwargs = {
            "signature": "blockquote:p:cite:",
        }
        block = block_quote(html, **kwargs)
        self.assertEqual(block["type"], "block_quote")
        self.assertEqual(block["value"]["quote"], "<p>Quote</p>")
        self.assertEqual(block["value"]["attribution"], "<cite>Attribution</cite>")

    def test_blockquote_text(self):
        html = "<blockquote>Quote</blockquote>"
        kwargs = {
            "signature": "blockquote:",
        }
        block = block_quote(html, **kwargs)
        self.assertEqual(block["type"], "block_quote")
        self.assertEqual(block["value"]["quote"], "Quote")
        self.assertEqual(block["value"]["attribution"], "")


class TestEmbed(SimpleTestCase):
    def test_embed(self):
        html = '<iframe src="https://www.youtube.com/random-code"></iframe>'
        block = embed(html)
        self.assertEqual(block["type"], "embed")
        self.assertEqual(block["value"], "https://youtu.be/random-code")


class TestDescription(SimpleTestCase):
    def test_description(self):
        html = "<dl><dt>Term</dt><dd>Description</dd></dl>"
        block = description(html)
        self.assertEqual(block["type"], "description")
        self.assertIsInstance(block["value"]["items"], list)
        self.assertEqual(block["value"]["items"][0]["term"], "Term")
        self.assertEqual(block["value"]["items"][0]["description"], "Description")

    def test_no_dl(self):
        html = "<dt>Term</dt><dd>Description</dd>"
        block = description(html)
        self.assertIsNone(block)

    def test_no_dt(self):
        html = "<dl><dd>Description</dd></dl>"
        block = description(html)
        self.assertIsNone(block)

    def test_no_dd(self):
        html = "<dl><dt>Term</dt></dl>"
        block = description(html)
        self.assertIsNone(block)

    def test_no_text(self):
        html = "<dl><dt></dt><dd></dd></dl>"
        block = description(html)
        self.assertEqual(block["type"], "description")
        self.assertIsInstance(block["value"]["items"], list)
        self.assertEqual(block["value"]["items"][0]["term"], "")
        self.assertEqual(block["value"]["items"][0]["description"], "")
