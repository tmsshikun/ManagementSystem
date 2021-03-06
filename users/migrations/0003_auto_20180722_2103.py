# Generated by Django 2.0.5 on 2018-07-22 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20180722_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='department',
            field=models.CharField(blank=True, choices=[('math', '数学科学学院'), ('physical', '物理与材料科学学院'), ('chemistry', '化学化工学院'), ('computer', '计算机科学与技术学院'), ('electric', '电子信息工程学院'), ('life', '生命科学学院'), ('book', '文学院'), ('history', '历史系'), ('philosophy', '哲学系'), ('news', '新闻传播学院'), ('economy', '经济学院'), ('business', '商学院'), ('foreign', '外语学院'), ('logic', '法学院'), ('manage', '管理学院'), ('society', '社会与政治学院'), ('art', '艺术学院'), ('environment', '资源与环境工程学院'), ('automate', '电气工程与自动化学院'), ('wengdian', '文典学院')], max_length=20, verbose_name='所在院系名称'),
        ),
    ]
