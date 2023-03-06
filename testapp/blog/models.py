from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.search import index

from wagtail_toolbox.wordpress.models.abstracts import BaseBlogPage


class BlogPage(BaseBlogPage):
    date = models.DateField("Post date", null=True)

    search_fields = Page.search_fields + [
        index.SearchField("content"),
        index.SearchField("excerpt"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]

    content_panels = BaseBlogPage.content_panels + [
        FieldPanel("date"),
    ]


class BlogIndexPage(BaseBlogPage):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]

    content_panels = BaseBlogPage.content_panels

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by("-first_published_at")
        context["blogpages"] = blogpages
        return context


# @register_snippet
# class Category(models.Model):
#     name = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)

#     panels = [
#         FieldPanel("name"),
#         FieldPanel("slug"),
#     ]

#     def __str__(self):
#         return self.name
