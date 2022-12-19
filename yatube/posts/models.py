from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
        verbose_name_plural="Заголовки",
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        verbose_name="Адрес",
        verbose_name_plural="Адреса",
    )
    description = models.TextField(
        verbose_name="Описание",
        verbose_name_plural="Описания",
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Статья",
        verbose_name_plural="Статьи",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        verbose_name_plural="Даты публикации",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
        verbose_name_plural="Авторы",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="groups",
        blank=True,
        null=True,
        verbose_name="Группа",
        verbose_name_plural="Группы",
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
