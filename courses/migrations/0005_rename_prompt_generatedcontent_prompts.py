# Generated by Django 3.2.9 on 2024-02-13 20:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_generatedcontent_response'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generatedcontent',
            old_name='prompt',
            new_name='prompts',
        ),
    ]
