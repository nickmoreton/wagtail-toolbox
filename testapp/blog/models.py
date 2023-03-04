from wagtail.models import Page

from wagtail_toolbox.wordpress.models.pages import AbstractPage


class BaseBlogPage(AbstractPage):
    """
    Base page model for all app page models that
    will be created from imported wordpress data.
    """

    class Meta:
        abstract = True


class BlogPage(BaseBlogPage):
    parent_page_types = ["blog.BlogIndexPage"]
    content_panels = BaseBlogPage.content_panels


class BlogIndexPage(Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]
