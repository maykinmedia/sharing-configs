# Generated by Django 4.0.4 on 2022-06-15 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sharing_configs", "0004_alter_sharingconfigsconfig_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sharingconfigsconfig",
            options={"verbose_name": "Sharing Configs configuration"},
        ),
        migrations.AlterField(
            model_name="sharingconfigsconfig",
            name="api_endpoint",
            field=models.URLField(
                help_text="Path to API point. For example: https://www.example.com/api/v1/",
                max_length=250,
                verbose_name="API endpoint",
            ),
        ),
        migrations.AlterField(
            model_name="sharingconfigsconfig",
            name="api_key",
            field=models.CharField(
                help_text="API key for authorization",
                max_length=128,
                verbose_name="API key",
            ),
        ),
        migrations.AlterField(
            model_name="sharingconfigsconfig",
            name="default_organisation",
            field=models.CharField(
                blank=True,
                help_text="The default organisation to use in the description when sharing configurations.",
                max_length=100,
                verbose_name="default organisation",
            ),
        ),
        migrations.AlterField(
            model_name="sharingconfigsconfig",
            name="label",
            field=models.CharField(
                help_text="This label should match the label in the Sharing Configs API.",
                max_length=50,
                verbose_name="label",
            ),
        ),
    ]
