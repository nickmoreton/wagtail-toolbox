# Generated by Django 4.1.7 on 2023-03-03 21:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wordpress", "0003_rename_tag_wptag"),
    ]

    operations = [
        migrations.CreateModel(
            name="WPAuthor",
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
                ("name", models.CharField(max_length=255)),
                ("url", models.URLField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("link", models.URLField()),
                ("slug", models.SlugField()),
                ("avatar_urls", models.URLField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Author",
                "verbose_name_plural": "Authors",
            },
        ),
    ]
