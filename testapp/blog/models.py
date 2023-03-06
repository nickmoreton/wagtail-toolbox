from datetime import datetime

from django import forms
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class BaseBlogPage(models.Model):
    content = RichTextField(blank=True)
    excerpt = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("content"),
        index.SearchField("excerpt"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("content"),
        FieldPanel("excerpt"),
    ]

    class Meta:
        abstract = True


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]

    content_panels = [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blog_pages = self.get_children().live().order_by("-first_published_at")
        context["blog_pages"] = blog_pages
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "BlogPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class BlogPage(BaseBlogPage, Page):
    date = models.DateTimeField("Post date", default=datetime.now)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)

    content_panels = BaseBlogPage.content_panels + [
        InlinePanel("gallery_images", label="Gallery images"),
        FieldPanel("date"),
        FieldPanel("tags"),
        FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
    ]

    parent_page_types = ["blog.BlogIndexPage"]

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(
        BlogPage, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class BlogTagIndexPage(Page):
    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get("tag")
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context["blogpages"] = blogpages
        return context


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("icon"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog category"
        verbose_name_plural = "Blog categories"


@register_snippet
class BlogAuthor(models.Model):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog author"
        verbose_name_plural = "Blog authors"
