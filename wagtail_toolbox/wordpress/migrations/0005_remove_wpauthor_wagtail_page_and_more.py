# Generated by Django 4.1.7 on 2023-03-14 17:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wordpress", "0004_wpauthor_wagtail_page_wpcategory_wagtail_page_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wpauthor",
            name="wagtail_page",
        ),
        migrations.RemoveField(
            model_name="wpcategory",
            name="wagtail_page",
        ),
        migrations.RemoveField(
            model_name="wpcomment",
            name="wagtail_page",
        ),
        migrations.RemoveField(
            model_name="wpmedia",
            name="wagtail_page",
        ),
        migrations.RemoveField(
            model_name="wppage",
            name="wagtail_page",
        ),
        migrations.RemoveField(
            model_name="wppost",
            name="wagtail_page",
        ),
        migrations.RemoveField(
            model_name="wptag",
            name="wagtail_page",
        ),
        migrations.AddField(
            model_name="wpauthor",
            name="wagtail_model",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wpcategory",
            name="wagtail_model",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wpcomment",
            name="wagtail_model",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wpmedia",
            name="wagtail_model",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wppage",
            name="wagtail_model",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wppost",
            name="wagtail_model",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wptag",
            name="wagtail_model",
            field=models.JSONField(blank=True, null=True),
        ),
    ]