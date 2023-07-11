# Generated by Django 3.2.2 on 2023-07-08 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0027_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='full_name',
            field=models.CharField(default='Default Full Name', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_authorized',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='saved_jobs',
            field=models.ManyToManyField(blank=True, to='jobs.JobListing'),
        ),
    ]
