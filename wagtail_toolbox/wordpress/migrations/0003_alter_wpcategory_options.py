# Generated by Django 4.1.7 on 2023-03-10 07:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wordpress", "0002_alter_wpcategory_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="wpcategory",
            options={"verbose_name": "Category", "verbose_name_plural": "Categories"},
        ),
    ]