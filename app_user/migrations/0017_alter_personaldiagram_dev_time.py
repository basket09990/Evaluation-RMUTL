# Generated by Django 5.0.6 on 2024-10-19 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0016_userworkloadselection_selected_workload_edit_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personaldiagram',
            name='dev_time',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]