# Generated by Django 4.0.3 on 2022-06-01 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sharing_configs", "0003_alter_sharingconfigsconfig_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sharingconfigsconfig",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
