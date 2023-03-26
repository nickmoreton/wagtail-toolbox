from bs4 import BeautifulSoup
from django.conf import settings


class HTMLCleaner:
    def clean_html(self, html_data=None, clean_tags=None):
        if not clean_tags:
            clean_tags = getattr(settings, "WPI_CLEAN_TAGS", ["div"])

        if html_data:
            soup = BeautifulSoup(html_data, "html.parser")
            # find all clean_tags tag name and remove them while keeping their contents
            for div in soup.find_all(clean_tags):
                div.unwrap()
            return str(soup)
