from django.contrib.auth import get_user_model
from django.db import models

from .constants import CHARS_LIMIT_COMMENT, CHARS_LIMIT_POST

User = get_user_model()


class Group(models.Model):
    description = models.TextField(
        verbose_name="Описание",
        help_text="Задайте описание для группы",
    )
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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("title",)
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):
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
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите текст поста",
    )
    image = models.ImageField(
        verbose_name="Картинка",
        help_text="Добавьте изображение для поста",
        upload_to="posts/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.text[:CHARS_LIMIT_POST]

    class Meta:
        ordering = ("-pub_date",)
        default_related_name = "posts"
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name="Пост",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name="Текст коментария",
        help_text="Введите текст коментария"
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )

    def __str__(self):
        return self.text[:CHARS_LIMIT_COMMENT]

    class Meta:
        ordering = ("-created",)
        default_related_name = "comments"
        verbose_name = "Коментарий"
        verbose_name_plural = "Коментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following",
    )

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
