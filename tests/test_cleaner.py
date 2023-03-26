from bs4 import BeautifulSoup as bs4
from django.test import TestCase

from wagtail_toolbox.wordpress.content_cleaner import ContentCleaner


class TestSignatureMethods(TestCase):
    def setUp(self):
        super().setUp()

        self.cls = ContentCleaner()

    def test_make_tag_signature(self):
        """Pass in a soup object and get a string signature back."""

        content = (
            "<p><strong>This should be left in place without any changes</strong></p>"
        )
        soup = bs4(content, "html.parser").find()
        signature = self.cls.make_tag_signature(soup)
        self.assertTrue(signature == "p:strong:")

        content = (
            "<h2><strong>This should be left in place without any changes</strong></h2>"
        )
        soup = bs4(content, "html.parser").find()
        signature = self.cls.make_tag_signature(soup)
        self.assertTrue(signature == "h2:strong:")

        content = "<div><strong>This should be left in place without any changes</strong></div>"
        soup = bs4(content, "html.parser").find()
        signature = self.cls.make_tag_signature(soup)
        self.assertTrue(signature == "div:strong:")

        content = (
            "<p><strong><a href="
            ">This</a> should be left in place without any changes</strong></p>"
        )
        soup = bs4(content, "html.parser").find()
        signature = self.cls.make_tag_signature(soup)
        self.assertTrue(signature == "p:strong:a:")

        content = """<p>
            <strong>lorem ipsum</strong>
            <a href="https://www.google.com">This</a>
            <strong>should be left in place without any changes</strong>
            </p>"""
        soup = bs4(content, "html.parser").find()
        signature = self.cls.make_tag_signature(soup)
        self.assertTrue(signature == "p:strong:")


class TestConverters(TestCase):
    """The format of the input html matters here.
    Make sure the html that is expected in cleand is on one line."""

    def setUp(self):
        self.cls = ContentCleaner()

    def test_promote_child(self):
        content_1_deep = """
        <div>
            <p><strong>Pellentesque Consectetur Etiam</strong></p>
        </div>"""
        cleaned = self.cls.promote_child(bs4(content_1_deep, "html.parser"), depth=1)
        self.assertTrue(
            str(cleaned) == "<p><strong>Pellentesque Consectetur Etiam</strong></p>"
        )

        content_2_deep = """
        <div>
            <div>
                <figure><img src="image.jpg" /><figcaption></figcaption></figure>
            </div>
        </div>"""
        cleaned = self.cls.promote_child(bs4(content_2_deep, "html.parser"), depth=2)
        self.assertTrue(
            str(cleaned)
            == '<figure><img src="image.jpg"/><figcaption></figcaption></figure>'
        )

    def test_make_paragraph(self):
        content = """<div>Pellentesque Consectetur Etiam</div>"""
        cleaned = self.cls.make_paragraph(bs4(content, "html.parser"))
        self.assertTrue(str(cleaned) == "<p>Pellentesque Consectetur Etiam</p>")


# class TestCleaner(TestCase):
#     def setUp(self):
#         patterns = {
#             "div:": {
#                 "actions": [
#                     {
#                         "clean": [
#                             {"make_paragraph": {}},
#                         ]
#                     },
#                 ]
#             },
#             "div:p:strong:": {
#                 "actions": [
#                     {
#                         "clean": [
#                             {"promote_child": {"kwargs": {"depth": 1}}},
#                         ]
#                     },
#                 ]
#             },
#             "div:figure:img:": {
#                 "actions": [
#                     {
#                         "clean": [
#                             {"promote_child": {"kwargs": {"depth": 1}}},
#                         ]
#                     },
#                 ]
#             },
#             "div:div:figure": {
#                 "actions": [
#                     {
#                         "clean": [
#                             {"promote_child": {"kwargs": {"depth": 2}}},
#                         ]
#                     },
#                 ]
#             },
#         }
#         self.cls = ContentCleaner(patterns=patterns)

# def test_clean_html(self):
#     cleaned = self.cls.clean("""<div>lorem</div>""")
#     self.assertTrue(str(cleaned) == "<p>lorem</p>")

#     cleaned = self.cls.clean(
#         """<div><p><strong>Pellentesque Consectetur Etiam</strong></p></div>"""
#     )
#     self.assertTrue(
#         str(cleaned) == "<p><strong>Pellentesque Consectetur Etiam</strong></p>"
#     )

# cleaned = self.cls.clean("""<div><figure><img src="image.jpg" /><figcaption></figcaption></figure></div>""")
# self.assertTrue(str(cleaned) == '<figure><img src="image.jpg"/><figcaption></figcaption></figure>')

# cleaned = self.cls.clean("""<div><div><figure><img src="image.jpg" /><figcaption></figcaption></figure></div><
# /div>""")
# print(cleaned)
# self.assertTrue(str(cleaned) == '<figure><img src="image.jpg"/><figcaption></figcaption></figure>')

# cleaned = self.cls.clean("""<div>lorem ipsum</div>""")
# self.assertTrue(str(cleaned) == "<p>lorem ipsum</p>")

# """<div>single div</div>
# <div>
#     <div>double div</div>
# </div>"""
# <p><strong>strong text</strong></p>
# <ul>
#     <li>list item</li>
#     <li>list item</li>
# </ul>
# <div>
#     <figure>
#         <img src="image.jpg" />
#         <figcaption>a caption in single div</figcaption>
#     </figure>
# </div>
# <div>
#     <div>
#         <figure>
#             <img src="image.jpg" />
#             <figcaption>a caption in double div</figcaption>
#         </figure>
#     </div>
# </div>"""
# # )
# soup = bs4(cleaned, "html.parser")
# self.assertTrue(soup.find("p", recursive=True))
# self.assertFalse(soup.find("div", recursive=True))
