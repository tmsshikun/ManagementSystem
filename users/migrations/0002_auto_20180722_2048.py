# Generated by Django 2.0.5 on 2018-07-22 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='department',
            field=models.CharField(blank=True, choices=[('computer', '计算机科学与技术'), ('art', '艺术学院')], max_length=20, verbose_name='所在院系名称'),
        ),
    ]
