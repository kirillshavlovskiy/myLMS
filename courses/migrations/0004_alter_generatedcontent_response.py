# Generated by Django 3.2.9 on 2024-02-13 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_auto_20240213_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatedcontent',
            name='response',
            field=models.TextField(),
        ),
    ]
