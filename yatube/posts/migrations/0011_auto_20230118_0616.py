# Generated by Django 2.2.16 on 2023-01-18 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20230116_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Добавьте изображение для поста', null=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]