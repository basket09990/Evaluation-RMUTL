# Generated by Django 5.0.6 on 2024-09-30 07:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0002_userselectedsubfield_evaluation'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_competency_ceo',
            name='evaluation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app_user.user_evaluation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user_competency_councilde',
            name='evaluation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app_user.user_evaluation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user_competency_main',
            name='evaluation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app_user.user_evaluation'),
            preserve_default=False,
        ),
    ]
