# Generated by Django 3.2.2 on 2023-06-28 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0018_alter_joblisting_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joblisting',
            name='date_posted',
            field=models.DateTimeField(blank=True, default='%B %d,%Y', null=True),
        ),
    ]