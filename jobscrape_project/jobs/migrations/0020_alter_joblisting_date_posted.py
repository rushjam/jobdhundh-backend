# Generated by Django 3.2.2 on 2023-06-28 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0019_alter_joblisting_date_posted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joblisting',
            name='date_posted',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]