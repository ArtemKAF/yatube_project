from django.contrib.auth import get_user_model
from django.db import models

from .constants import CHARS_LIMIT_POST

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
        help_text="Укажите заголовок группы",
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        verbose_name="Адрес",
        help_text="Короткий, уникальный адрес группы",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Задайте описание для группы",
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ("title",)
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите текст поста",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )

    def __str__(self) -> str:
        return self.text[:CHARS_LIMIT_POST]

    class Meta:
        ordering = ("-pub_date",)
        default_related_name = "posts"
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
