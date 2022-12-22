from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, db_index=True, verbose_name="Адрес")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title
    
class Post(models.Model):
    text = models.TextField(verbose_name="Статья")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='groups',
        blank=True,
        null=True,
        verbose_name="Группа"
    )
