# Generated by Django 4.1.7 on 2023-03-04 01:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wordpress", "0005_wppost"),
    ]

    operations = [
        migrations.AddField(
            model_name="wpauthor",
            name="wp_many_to_many_keys",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wpcategory",
            name="wp_many_to_many_keys",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wppost",
            name="wp_many_to_many_keys",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wptag",
            name="wp_many_to_many_keys",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
