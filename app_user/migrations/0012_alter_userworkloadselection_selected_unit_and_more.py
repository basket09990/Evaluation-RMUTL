# Generated by Django 5.0.6 on 2024-10-11 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0011_alter_profile_administrative_position_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userworkloadselection',
            name='selected_unit',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='workloadcriteria',
            name='c_unit',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]