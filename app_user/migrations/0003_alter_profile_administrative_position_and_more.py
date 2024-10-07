# Generated by Django 5.0.6 on 2024-10-06 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0002_alter_profile_start_goverment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='administrative_position',
            field=models.TextField(blank=True, default='', null=True, verbose_name='ตำแหน่งบริหาร'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='affiliation',
            field=models.TextField(blank=True, default='', null=True, verbose_name='สังกัด'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='days_of_service',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='months_of_service',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='old_government',
            field=models.TextField(blank=True, default='', null=True, verbose_name='มาช่วยราชการจากที่ใด (ถ้ามี)'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='position_number',
            field=models.TextField(blank=True, default='', null=True, verbose_name='เลขที่ประจำตำแหน่ง'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='salary',
            field=models.TextField(blank=True, default='', null=True, verbose_name='เงินเดือน'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='special_position',
            field=models.TextField(blank=True, default='', null=True, verbose_name='หน้าที่พิเศษ'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='start_goverment',
            field=models.TextField(blank=True, default='', null=True, verbose_name='เริ่มรับราชการเมื่อวันที่'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='sum_time_goverment',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='years_of_service',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]