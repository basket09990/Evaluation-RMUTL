# Generated by Django 5.0.6 on 2024-09-30 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0003_user_competency_ceo_evaluation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_competency_ceo',
            name='actual_score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='user_competency_councilde',
            name='actual_score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='user_competency_main',
            name='actual_score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
