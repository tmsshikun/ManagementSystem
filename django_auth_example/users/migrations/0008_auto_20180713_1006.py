# Generated by Django 2.0.5 on 2018-07-13 02:06

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20180712_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='english_name',
            field=jsonfield.fields.JSONField(),
        ),
    ]
