from django.contrib import admin
from django.utils.safestring import mark_safe

from wagtail_toolbox.wordpress.models import (
    WPAuthor,
    WPCategory,
    WPComment,
    WPMedia,
    WPPage,
    WPPost,
    WPTag,
)


class WordpressImportAdminSite(admin.AdminSite):
    # Admin site for the imported wordpress data
    site_header = "Wordpress Import Admin"
    site_title = "Wordpress Import Admin Portal"
    index_title = "Welcome to the Wordpress Import Admin Portal"


wordpress_import_admin_site = WordpressImportAdminSite(name="wordpress-import-admin")


class BaseAdmin(admin.ModelAdmin):
    """
    Base admin class for all wordpress models

    This class provides some common functionality for all wordpress models.
    It's main purpose is to keep the admin list_display pages clean and easy to read.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.truncated_length = 12

        first_fields = ["name", "title", "author_name"]
        last_fields = ["wp_id", "wp_foreign_keys", "wp_many_to_many_keys"]

        truncated_fields = [
            "title",
            "name",
            "content",
            "excerpt",
            "description",
            "caption",
        ]

        remove_fields = [
            "wp_foreign_keys",
            "wp_many_to_many_keys",
            "author_avatar_urls",
            "avatar_urls",
        ]

        link_fields = ["guid", "link", "source_url"]

        self.list_display = self.get_list_display_fields(
            self.model,
            remove_fields,
            first_fields,
            last_fields,
            truncated_fields,
            link_fields,
        )
        self.search_fields = [
            field.name
            for field in self.model._meta.fields
            if field.name in first_fields
        ]

    def get_list_display_fields(
        self,
        obj,
        remove_fields,
        first_fields,
        last_fields,
        truncated_fields,
        link_fields,
    ):
        """
        Return the list_display fields for a model

        This method is used to add some common functionality to the admin list_display pages.

        1. add some column ordering
        2. truncate some overly long fields
        3. remove some fields
        4. add some links to open the original wordpress content
        """
        fields = [field.name for field in obj._meta.fields]

        for field in first_fields:
            if field in fields:
                fields.remove(field)
                fields.insert(0, field)

        for field in last_fields:
            if field in fields:
                fields.remove(field)
                fields.append(field)

        for field in truncated_fields:
            if field in fields:
                position = fields.index(field)
                fields.insert(position, f"get_truncated_{field}")
                fields.remove(field)

        for field in remove_fields:
            if field in fields:
                fields.remove(field)

        for field in link_fields:
            if field in fields:
                position = fields.index(field)
                fields.insert(position, f"get_link_{field}")
                fields.remove(field)

        return fields

    def get_truncated_content(self, obj):
        return (
            obj.content[: self.truncated_length] + "..."
            if len(obj.content) > self.truncated_length
            else obj.content
        )

    get_truncated_content.short_description = "Content"

    def get_truncated_excerpt(self, obj):
        return (
            obj.excerpt[: self.truncated_length] + "..."
            if len(obj.excerpt) > self.truncated_length
            else obj.excerpt
        )

    get_truncated_excerpt.short_description = "Excerpt"

    def get_truncated_description(self, obj):
        return (
            obj.description[: self.truncated_length] + "..."
            if len(obj.description) > self.truncated_length
            else obj.description
        )

    get_truncated_description.short_description = "Description"

    def get_truncated_caption(self, obj):
        return (
            obj.caption[: self.truncated_length] + "..."
            if len(obj.caption) > self.truncated_length
            else obj.caption
        )

    get_truncated_caption.short_description = "Caption"

    def get_truncated_title(self, obj):
        return (
            obj.title[: self.truncated_length] + "..."
            if len(obj.title) > self.truncated_length
            else obj.title
        )

    get_truncated_title.short_description = "Title"

    def get_truncated_name(self, obj):
        return (
            obj.name[: self.truncated_length] + "..."
            if len(obj.name) > self.truncated_length
            else obj.name
        )

    get_truncated_name.short_description = "Name"

    def get_link_guid(self, obj):
        guid = obj.guid
        guid = f'<a href="{guid}" target="_blank">Open</a>'
        return mark_safe(guid)

    get_link_guid.short_description = "Guid"

    def get_link_link(self, obj):
        link = obj.link
        link = f'<a href="{link}" target="_blank">Open</a>'
        return mark_safe(link)

    get_link_link.short_description = "Link"

    def get_link_source_url(self, obj):
        source_url = obj.source_url
        source_url = f'<a href="{source_url}" target="_blank">Open</a>'
        return mark_safe(source_url)

    get_link_source_url.short_description = "Source Url"


wordpress_import_admin_site.register(WPPage, BaseAdmin)
wordpress_import_admin_site.register(WPCategory, BaseAdmin)
wordpress_import_admin_site.register(WPTag, BaseAdmin)


# class AuthorAdmin(BaseAdmin):
#     list_display = (
#         "name",
#         "id",
#         "wp_id",
#         "get_link",
#         "slug",
#         "description",
#         "get_avatar_urls",
#         "url",
#     )
#     search_fields = ("name", "description")

#     def get_link(self, obj):
#         link = obj.link
#         if len(link) > 50:
#             return link[:50] + "..."
#         return obj.link

#     def get_avatar_urls(self, obj):
#         avatar = obj.avatar_urls
#         if len(avatar) > 50:
#             return avatar[:50] + "..."
#         return obj.avatar_urls


wordpress_import_admin_site.register(WPAuthor, BaseAdmin)


# class PostAdmin(BaseAdmin):
#     list_display = (
#         "get_title",
#         "id",
#         "wp_id",
#         "date",
#         "date_gmt",
#         "guid",
#         "modified",
#         "modified_gmt",
#         "slug",
#         "status",
#         "type",
#         "link",
#         "get_content",
#         "get_excerpt",
#         "author",
#         "comment_status",
#         "ping_status",
#         "sticky",
#         "format",
#         "template",
#     )
#     search_fields = ("title", "content", "excerpt")
#     filter_horizontal = ("categories", "tags")

#     def get_title(self, obj):
#         title = obj.title
#         if len(title) > 30:
#             return title[:30] + "..."
#         return obj.title

#     def get_content(self, obj):
#         content = obj.content
#         if len(content) > 50:
#             return content[:50] + "..."
#         return obj.content

#     def get_excerpt(self, obj):
#         excerpt = obj.excerpt
#         if len(excerpt) > 50:
#             return excerpt[:50] + "..."
#         return obj.excerpt


wordpress_import_admin_site.register(WPPost, BaseAdmin)


# class CommentAdmin(BaseAdmin):
#     list_display = (
#         "author_name",
#         "author_url",
#         "author",
#         "id",
#         "wp_id",
#         "post",
#         "parent",
#         "date",
#         "date_gmt",
#         "get_content",
#         "link",
#         "status",
#         "author_avatar_urls",
#     )
#     search_fields = ("author_name",)

#     def get_content(self, obj):
#         content = obj.content
#         if len(content) > 50:
#             return content[:50] + "..."
#         return obj.content


wordpress_import_admin_site.register(WPComment, BaseAdmin)


# class MediaAdmin(BaseAdmin):
#     list_display = (
#         "title",
#         "id",
#         "wp_id",
#         "date",
#         "date_gmt",
#         "guid",
#         "modified",
#         "modified_gmt",
#         "slug",
#         "get_description",
#         "get_caption",
#         "alt_text",
#         "source_url",
#     )
#     search_fields = ("title", "description", "caption")

#     def get_description(self, obj):
#         desc = obj.description
#         if len(desc) > 50:
#             return desc[:50] + "..."
#         return obj.description

#     def get_caption(self, obj):
#         caption = obj.caption
#         if len(caption) > 50:
#             return caption[:50] + "..."
#         return obj.caption


wordpress_import_admin_site.register(WPMedia, BaseAdmin)
