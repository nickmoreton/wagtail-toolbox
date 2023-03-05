from django.contrib import admin

from wagtail_toolbox.wordpress.models import (
    WPAuthor,
    WPCategory,
    WPComment,
    WPMedia,
    WPPage,
    WPPost,
    WPTag,
)

# from wagtail_toolbox.wordpress.views import import_wordpress_data_django_admin_view
# from django.template.response import TemplateResponse
# from django.urls import path


"""
Admin site for the imported wordpress data
"""


class PageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "wp_id",
        "link",
        "slug",
        "status",
        "author",
        "parent",
        "comment_status",
        "ping_status",
        "template",
    )
    search_fields = ("title", "content", "excerpt")

    class Media:
        css = {"all": ("css/wordpress.css",)}


admin.site.register(WPPage, PageAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "wp_id",
        "count",
        "link",
        "slug",
        "description",
        "parent",
        "taxonomy",
    )
    search_fields = ("name", "description")


admin.site.register(WPCategory, CategoryAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "wp_id", "count", "link", "slug", "description", "taxonomy")
    search_fields = ("name", "description")


admin.site.register(WPTag, TagAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "wp_id",
        "get_link",
        "slug",
        "description",
        "get_avatar_urls",
        "url",
    )
    search_fields = ("name", "description")

    def get_link(self, obj):
        link = obj.link
        if len(link) > 50:
            return link[:50] + "..."
        return obj.link

    def get_avatar_urls(self, obj):
        avatar = obj.avatar_urls
        if len(avatar) > 50:
            return avatar[:50] + "..."
        return obj.avatar_urls


admin.site.register(WPAuthor, AuthorAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "get_title",
        "id",
        "wp_id",
        "date",
        "date_gmt",
        "guid",
        "modified",
        "modified_gmt",
        "slug",
        "status",
        "type",
        "link",
        "get_content",
        "get_excerpt",
        "author",
        "comment_status",
        "ping_status",
        "sticky",
        "format",
        "template",
    )
    search_fields = ("title", "content", "excerpt")
    filter_horizontal = ("categories", "tags")

    def get_title(self, obj):
        title = obj.title
        if len(title) > 30:
            return title[:30] + "..."
        return obj.title

    def get_content(self, obj):
        content = obj.content
        if len(content) > 50:
            return content[:50] + "..."
        return obj.content

    def get_excerpt(self, obj):
        excerpt = obj.excerpt
        if len(excerpt) > 50:
            return excerpt[:50] + "..."
        return obj.excerpt


admin.site.register(WPPost, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "author_name",
        "author_url",
        "author",
        "id",
        "wp_id",
        "post",
        "parent",
        "date",
        "date_gmt",
        "get_content",
        "link",
        "status",
        "author_avatar_urls",
    )
    search_fields = ("author_name",)

    def get_content(self, obj):
        content = obj.content
        if len(content) > 50:
            return content[:50] + "..."
        return obj.content


admin.site.register(WPComment, CommentAdmin)


class MediaAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "id",
        "wp_id",
        "date",
        "date_gmt",
        "guid",
        "modified",
        "modified_gmt",
        "slug",
        "get_description",
        "get_caption",
        "alt_text",
        "source_url",
    )
    search_fields = ("title", "description", "caption")

    def get_description(self, obj):
        desc = obj.description
        if len(desc) > 50:
            return desc[:50] + "..."
        return obj.description

    def get_caption(self, obj):
        caption = obj.caption
        if len(caption) > 50:
            return caption[:50] + "..."
        return obj.caption


admin.site.register(WPMedia, MediaAdmin)
