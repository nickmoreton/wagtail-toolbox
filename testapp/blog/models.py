from datetime import datetime

from django import forms
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from wagtail_toolbox.wordpress.blocks import BlogStreamBlocks


class BaseBlogPage(models.Model):
    content = StreamField(
        BlogStreamBlocks(),
        verbose_name="Page content",
        blank=True,
        use_json_field=True,
        null=True,
    )
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

    content_panels = Page.content_panels + [
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
    author = models.ForeignKey(
        "blog.BlogAuthor",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    content_panels = BaseBlogPage.content_panels + [
        InlinePanel("gallery_images", label="Gallery images"),
        FieldPanel("date"),
        FieldPanel("tags"),
        FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
        FieldPanel("author"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = ["blog.BlogComment"]

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


class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=["name", "slug"], null=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog category"
        verbose_name_plural = "Blog categories"


class BlogCategoryViewSet(SnippetViewSet):
    list_display = ("name", "slug")


register_snippet(BlogCategory, BlogCategoryViewSet)


class BlogAuthor(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog author"
        verbose_name_plural = "Blog authors"


class BlogAuthorViewSet(SnippetViewSet):
    list_display = ("name", "slug")


register_snippet(BlogAuthor, BlogAuthorViewSet)


class BlogComment(Page):
    """A comment on a blog post."""

    # author name will be the title
    date = models.DateTimeField("Comment date", default=datetime.now)
    content = RichTextField(blank=True)
    # status will be published or unpublished

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("content"),
    ]

    parent_page_types = ["blog.BlogPage", "blog.BlogComment"]
