# from bs4 import BeautifulSoup as bs4
# from django.test import TestCase

# from wagtail_toolbox.wordpress.utils import make_signature

# class TestUtils(TestCase):
#     def setUp(self):
#         super().setUp()

#         with open("tests/fixtures/test_cleaner.html") as f:
#             self.content = f.read()

#     def test_make_signature(self):
#         soup = bs4(self.content, "html.parser").findChildren(recursive=False)
#         for tag in soup:
#             signature = make_signature(tag)
#             print(signature)
