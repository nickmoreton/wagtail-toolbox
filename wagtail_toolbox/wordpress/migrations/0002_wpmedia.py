# Generated by Django 4.1.7 on 2023-03-04 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wordpress", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WPMedia",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "wp_id",
                    models.IntegerField(unique=True, verbose_name="Wordpress ID"),
                ),
                ("wp_foreign_keys", models.JSONField(blank=True, null=True)),
                ("wp_many_to_many_keys", models.JSONField(blank=True, null=True)),
                ("title", models.CharField(max_length=255)),
                ("date", models.DateTimeField()),
                ("date_gmt", models.DateTimeField()),
                ("guid", models.URLField()),
                ("modified", models.DateTimeField()),
                ("modified_gmt", models.DateTimeField()),
                ("slug", models.SlugField()),
                ("status", models.CharField(max_length=255)),
                ("comment_status", models.CharField(max_length=255)),
                ("ping_status", models.CharField(max_length=255)),
                ("type", models.CharField(max_length=255)),
                ("link", models.URLField()),
                ("template", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("caption", models.TextField()),
                ("alt_text", models.CharField(max_length=255)),
                ("media_type", models.CharField(max_length=255)),
                ("mime_type", models.CharField(max_length=255)),
                ("source_url", models.URLField()),
                (
                    "post",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wordpress.wppost",
                    ),
                ),
            ],
            options={
                "verbose_name": "Media",
                "verbose_name_plural": "Media",
            },
        ),
    ]
