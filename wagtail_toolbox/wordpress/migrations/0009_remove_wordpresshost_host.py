# Generated by Django 4.1.7 on 2023-03-31 09:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wordpress", "0008_wordpressendpoint"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wordpresshost",
            name="host",
        ),
    ]
