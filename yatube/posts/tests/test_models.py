from django.test import TestCase

from ..constants import CHARS_LIMIT_COMMENT, CHARS_LIMIT_POST
from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост для тестов",
        )

    def test_posts_model_correct_str(self):
        """Проверяем, что у модели корректно работает __str__."""
        self.assertEqual(
            str(PostModelTest.post),
            PostModelTest.post.text[:CHARS_LIMIT_POST]
        )

    def test_posts_model_have_verbose_name(self):
        """Проверяем, что у модели задано человекочитаемое имя"""
        self.assertEqual(
            PostModelTest.post._meta.verbose_name,
            "Пост"
        )

    def test_posts_model_have_verbose_name_plural(self):
        """Проверяем, что у модели задано человекочитаемое имя во множественном
        числе
        """
        self.assertEqual(
            PostModelTest.post._meta.verbose_name_plural,
            "Посты"
        )

    def test_post_models_fields_have_verbose_name(self):
        """Проверяем, что у полей модели задано человекочитаемые имена"""
        for value, expected in {
            "text": "Текст поста",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
            "image": "Картинка",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_post_models_fields_have_help_text(self):
        """Проверяем, что у полей модели заданы подсказки"""
        for value, expected in {
            "text": "Введите текст поста",
            "group": "Группа, к которой будет относиться пост",
            "image": "Добавьте изображение для поста",
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
        cls.author = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост для тестов",
        )

    def test_groups_model_correct_str(self):
        """Проверяем, что у модели корректно работает __str__."""
        self.assertEqual(
            str(GroupModelTest.group),
            GroupModelTest.group.title
        )

    def test_groups_model_have_verbose_name(self):
        """Проверяем, что у модели задано человекочитаемое имя"""
        self.assertEqual(
            GroupModelTest.group._meta.verbose_name,
            "Группа"
        )

    def test_groups_model_have_verbose_name_plural(self):
        """Проверяем, что у модели задано человекочитаемое имя во множественном
        числе
        """
        self.assertEqual(
            GroupModelTest.group._meta.verbose_name_plural,
            "Группы"
        )

    def test_group_models_fields_have_verbose_name(self):
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

    def test_group_models_fields_have_help_text(self):
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


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="auth")
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост для тестов",
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text="коментарий тестового поста"
        )

    def test_comments_model_correct_str(self):
        """Проверяем, что у модели корректно работает __str__."""
        self.assertEqual(
            str(CommentModelTest.comment),
            CommentModelTest.comment.text[:CHARS_LIMIT_COMMENT]
        )

    def test_comments_model_have_verbose_name(self):
        """Проверяем, что у модели задано человекочитаемое имя"""
        self.assertEqual(
            CommentModelTest.comment._meta.verbose_name,
            "Коментарий"
        )

    def test_comments_model_have_verbose_name_plural(self):
        """Проверяем, что у модели задано человекочитаемое имя во множественном
        числе
        """
        self.assertEqual(
            CommentModelTest.comment._meta.verbose_name_plural,
            "Коментарии"
        )

    def test_comment_models_fields_have_verbose_name(self):
        """Проверяем, что у полей модели задано человекочитаемые имена"""
        for value, expected in {
            "post": "Пост",
            "author": "Автор",
            "text": "Текст коментария",
            "created": "Дата публикации",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    CommentModelTest.comment._meta.get_field(
                        value
                    ).verbose_name,
                    expected
                )

    def test_comment_models_fields_have_help_text(self):
        """Проверяем, что у полей модели заданы подсказки"""
        for value, expected in {
            "text": "Введите текст коментария",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    CommentModelTest.comment._meta.get_field(value).help_text,
                    expected
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="auth")
        cls.user = User.objects.create_user(username="use")
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_follows_model_correct_str(self):
        """Проверяем, что у модели корректно работает __str__."""
        self.assertEqual(
            str(FollowModelTest.follow),
            f"{FollowModelTest.follow.user} подписан "
            f"на {FollowModelTest.follow.author}"
        )

    def test_follows_model_have_verbose_name(self):
        """Проверяем, что у модели задано человекочитаемое имя"""
        self.assertEqual(
            FollowModelTest.follow._meta.verbose_name,
            "Подписка"
        )

    def test_follows_model_have_verbose_name_plural(self):
        """Проверяем, что у модели задано человекочитаемое имя во множественном
        числе
        """
        self.assertEqual(
            FollowModelTest.follow._meta.verbose_name_plural,
            "Подписки"
        )

    def test_follow_models_fields_have_verbose_name(self):
        """Проверяем, что у полей модели задано человекочитаемые имена"""
        for value, expected in {
            "user": "Подписчик",
            "author": "Автор",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    FollowModelTest.follow._meta.get_field(
                        value
                    ).verbose_name,
                    expected
                )

    def test_follow_models_fields_have_related_name(self):
        """Проверяем, что у полей модели заданы подсказки"""
        for value, expected in {
            "user": "follower",
            "author": "following",
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    FollowModelTest.follow._meta.get_field(
                        value
                    ).remote_field.related_name,
                    expected
                )
