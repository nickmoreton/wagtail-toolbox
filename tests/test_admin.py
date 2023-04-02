from unittest.mock import MagicMock

from django.test import TestCase, override_settings
from faker import Faker

from wagtail_toolbox.wordpress.admin import BaseAdmin

fake = Faker()


class TestBaseAdmin(TestCase):
    def setUp(self):
        paragraph = fake.paragraph(nb_sentences=2, variable_nb_sentences=False)
        sentence = fake.sentence(nb_words=6, variable_nb_words=False)
        url = fake.url()

        self.post = MagicMock()
        self.content = paragraph
        self.excerpt = paragraph
        self.description = paragraph
        self.caption = paragraph
        self.title = sentence
        self.name = sentence
        self.link_guid = url
        self.link_link = url
        self.link_source_url = url

        self.base_admin = BaseAdmin(
            model=MagicMock(),
            admin_site=MagicMock(),
        )

    def test_get_truncated_content(self):
        self.post.content = self.content
        self.assertEqual(
            self.base_admin.get_truncated_content(
                self.post,
            ),
            self.content[: self.base_admin.truncated_length] + "..."
            if len(self.content) > self.base_admin.truncated_length
            else self.content,
        )

    def test_get_truncated_excerpt(self):
        self.post.excerpt = self.excerpt
        self.assertEqual(
            self.base_admin.get_truncated_excerpt(
                self.post,
            ),
            self.excerpt[: self.base_admin.truncated_length] + "..."
            if len(self.excerpt) > self.base_admin.truncated_length
            else self.excerpt,
        )

    def test_get_truncated_description(self):
        self.post.description = self.description
        self.assertEqual(
            self.base_admin.get_truncated_description(
                self.post,
            ),
            self.description[: self.base_admin.truncated_length] + "..."
            if len(self.description) > self.base_admin.truncated_length
            else self.description,
        )

    def test_get_truncated_caption(self):
        self.post.caption = self.caption
        self.assertEqual(
            self.base_admin.get_truncated_caption(
                self.post,
            ),
            self.caption[: self.base_admin.truncated_length] + "..."
            if len(self.caption) > self.base_admin.truncated_length
            else self.caption,
        )

    def test_get_truncated_title(self):
        self.post.title = self.title
        self.assertEqual(
            self.base_admin.get_truncated_title(
                self.post,
            ),
            self.title[: self.base_admin.truncated_length] + "..."
            if len(self.title) > self.base_admin.truncated_length
            else self.title,
        )

    def test_get_truncated_name(self):
        self.post.name = self.name
        self.assertEqual(
            self.base_admin.get_truncated_name(
                self.post,
            ),
            self.name[: self.base_admin.truncated_length] + "..."
            if len(self.name) > self.base_admin.truncated_length
            else self.name,
        )

    def test_get_link_guid(self):
        self.assertEqual(
            self.base_admin.get_link_guid(
                self.post,
            ),
            f'<a href="{self.post.guid}" target="_blank">Open</a>',
        )

    def test_get_link_link(self):
        self.assertEqual(
            self.base_admin.get_link_link(
                self.post,
            ),
            f'<a href="{self.post.link}" target="_blank">Open</a>',
        )

    def test_get_link_source_url(self):
        self.assertEqual(
            self.base_admin.get_link_source_url(
                self.post,
            ),
            f'<a href="{self.post.source_url}" target="_blank">Open</a>',
        )

    @override_settings(
        WPI_TRUNCATE_LENGTH=10,
    )
    def test_get_truncated_content_with_truncate_length(self):
        self.post.content = self.content
        self.assertEqual(
            self.base_admin.get_truncated_content(
                self.post,
            ),
            self.content[: self.base_admin.truncated_length] + "..."
            if len(self.content) > self.base_admin.truncated_length
            else self.content,
        )


class TestBaseAdminOverride(TestCase):
    @override_settings(WPI_TRUNCATE_LENGTH=None)
    def test_init(self):
        base_admin = BaseAdmin(
            model=MagicMock(),
            admin_site=MagicMock(),
        )
        self.assertEqual(base_admin.truncated_length, 36)

    @override_settings(WPI_TRUNCATE_LENGTH=100)
    def test_init_with_truncate_length(self):
        base_admin = BaseAdmin(
            model=MagicMock(),
            admin_site=MagicMock(),
        )
        self.assertEqual(base_admin.truncated_length, 100)
