# Generated by Django 2.2.19 on 2022-11-29 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20221129_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=50),
        ),
    ]