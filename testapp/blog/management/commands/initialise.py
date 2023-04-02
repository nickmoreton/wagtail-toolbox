from django.core.management import BaseCommand

from testapp.blog.models import BlogIndexPage, BlogTagIndexPage
from testapp.home.models import HomePage


class Command(BaseCommand):
    help = "Initialise the Wgatail setup ready for importing from WordPress."

    def handle(self, *args, **options):
        # create the blog index page
        home_page = HomePage.objects.first()
        blog_index_page = BlogIndexPage(
            title="Blog",
            slug="blog",
            intro="A blog about all things Wagtail",
        )
        home_page.add_child(instance=blog_index_page)

        # create the tags index page
        blog_tag_index_page = BlogTagIndexPage(
            title="Tags",
            slug="tags",
        )
        home_page.add_child(instance=blog_tag_index_page)
