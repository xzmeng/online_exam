# Generated by Django 2.1.7 on 2019-04-03 10:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0015_auto_20190403_1748'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='response',
            options={'verbose_name': '学生成绩', 'verbose_name_plural': '学生成绩'},
        ),
        migrations.RemoveField(
            model_name='survey',
            name='display_by_question',
        ),
    ]
