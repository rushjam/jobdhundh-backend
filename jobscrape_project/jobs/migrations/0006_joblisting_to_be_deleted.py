# Generated by Django 4.2.2 on 2023-06-16 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_joblisting_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='to_be_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
