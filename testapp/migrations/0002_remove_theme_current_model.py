# Generated by Django 4.0.3 on 2022-06-13 05:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("testapp", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="theme",
            name="current_model",
        ),
    ]
