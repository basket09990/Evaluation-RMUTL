# Generated by Django 5.0.6 on 2024-10-10 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0009_alter_userworkloadselection_selected_maxnum_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userworkloadselection',
            name='selected_unit',
            field=models.FloatField(default='1'),
        ),
        migrations.AlterField(
            model_name='workloadcriteria',
            name='c_unit',
            field=models.FloatField(blank=True, default='1', null=True),
        ),
    ]