# Generated by Django 3.2.2 on 2023-06-18 22:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_auto_20230617_1836'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyJobCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_jobs', models.IntegerField(default=0)),
                ('today_posted_jobs', models.IntegerField(default=0)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_counts', to='jobs.company')),
            ],
        ),
    ]