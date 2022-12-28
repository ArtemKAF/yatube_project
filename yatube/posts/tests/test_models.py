from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post
from ..constants import CHARS_LIMIT_POST

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост для тестов",
        )

    def test_model_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(
            str(PostModelTest.post),
            PostModelTest.post.text[:CHARS_LIMIT_POST]
        )

    def test_model_have_verbose_name(self):
        """Проверяем, что у модели задано человекочитаемое имя"""
        self.assertEqual(
            PostModelTest.post._meta.verbose_name,
            "Пост"
        )

    def test_model_have_verbose_name_plural(self):
        """Проверяем, что у модели задано человекочитаемое имя во множественном
        числе
        """
        self.assertEqual(
            PostModelTest.post._meta.verbose_name_plural,
            "Посты"
        )

    def test_models_fields_have_verbose_name(self):
        """Проверяем, что у полей модели задано человекочитаемые имена"""
        for value, expected in {
            "text": "Текст поста",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_models_fields_have_help_text(self):
        """Проверяем, что у полей модели заданы подсказки"""
        for value, expected in {
            "text": "Введите текст поста",
            "group": "Группа, к которой будет относиться пост",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).help_text,
                    expected
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост для тестов",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(
            str(GroupModelTest.group),
            GroupModelTest.group.title
        )

    def test_models_have_verbose_name(self):
        """Проверяем, что у модели задано человекочитаемое имя"""
        self.assertEqual(
            GroupModelTest.group._meta.verbose_name,
            "Группа"
        )

    def test_models_have_verbose_name_plural(self):
        """Проверяем, что у модели задано человекочитаемое имя во множественном
        числе
        """
        self.assertEqual(
            GroupModelTest.group._meta.verbose_name_plural,
            "Группы"
        )

    def test_models_fields_have_verbose_name(self):
        """Проверяем, что у полей модели задано человекочитаемые имена"""
        for value, expected in {
            "title": "Заголовок",
            "slug": "Адрес",
            "description": "Описание",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    GroupModelTest.group._meta.get_field(value).verbose_name,
                    expected
                )

    def test_models_fields_have_help_text(self):
        """Проверяем, что у полей модели заданы подсказки"""
        for value, expected in {
            "title": "Укажите заголовок группы",
            "slug": "Короткий, уникальный адрес группы",
            "description": "Задайте описание для группы",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    GroupModelTest.group._meta.get_field(value).help_text,
                    expected
                )
