# Generated by Django 5.0.6 on 2024-10-14 09:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0013_evr_round_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evr_round',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]