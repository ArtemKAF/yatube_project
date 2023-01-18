import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post, User


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.author = User.objects.create_user(username="TestAuthor")
        cls.user = User.objects.create_user(username="TestUser")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            description="Группа для тестов",
            slug="test"
        )

        cls.picture = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.post = Post.objects.create(
            text="Текст поста для проверки",
            author=PostsCreateFormTests.author,
            group=PostsCreateFormTests.group,
            image=SimpleUploadedFile(
                name="test_smal.gif",
                content=PostsCreateFormTests.picture,
                content_type="image/gif"
            ),
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=PostsCreateFormTests.picture,
            content_type="image/gif"
        )
        self.form_data = {
            "text": "Пост для теста формы",
            "group": PostsCreateFormTests.group.pk,
            "image": uploaded,
        }
        self.posts_count = Post.objects.count()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsCreateFormTests.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostsCreateFormTests.author)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_form_attributes(self):
        """Проверяем атрибуты полей формы"""
        for field in PostForm._meta.fields:
            for attr, value in {
                Post._meta.get_field(field).verbose_name: "label",
                Post._meta.get_field(field).help_text: "help_text"
            }.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        PostsCreateFormTests.form.fields[
                            field
                        ].__dict__[value],
                        attr
                    )

    def test_create_post_authrized_client(self):
        """Проверяем создание поста авторизованным пользователем"""
        responce = self.authorized_client.post(
            reverse("posts:post_create"),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertRedirects(
            responce,
            reverse(
                "posts:profile",
                kwargs={"username": PostsCreateFormTests.user.username})
        )
        self.assertTrue(
            Post.objects.filter(
                text=self.form_data["text"],
                author=PostsCreateFormTests.user,
                group=self.form_data["group"],
                image="posts/small.gif"
            )
        )

    def test_create_post_guest_client(self):
        """Проверяем невозможность создания поста неавторизованным
        пользователем
        """
        response = self.guest_client.post(
            reverse("posts:post_create"),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_editing_post(self):
        """Проверяем редактирование поста"""
        responce = self.authorized_client_author.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": PostsCreateFormTests.post.id}
            ),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertRedirects(
            responce,
            reverse(
                "posts:post_details",
                kwargs={"post_id": PostsCreateFormTests.post.id})
        )
        self.assertTrue(
            Post.objects.filter(
                text=self.form_data["text"],
                author=PostsCreateFormTests.author,
                group=self.form_data["group"],
                image="posts/small.gif"
            )
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username="TestAuthor")
        cls.user = User.objects.create_user(username="TestUser")

        cls.post = Post.objects.create(
            text="Текст поста для проверки",
            author=CommentCreateFormTests.author,
        )

        cls.form_data = {
            "text": "Текст коментария для теста формы",
            "author": CommentCreateFormTests.user,
        }

        cls.form = CommentForm()

    def setUp(self):
        self.comment_count = Comment.objects.count()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentCreateFormTests.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(
            CommentCreateFormTests.author
        )

    def test_form_attributes(self):
        """Проверяем атрибуты полей формы"""
        for field in CommentForm._meta.fields:
            for attr, value in {
                Comment._meta.get_field(field).verbose_name: "label",
                Comment._meta.get_field(field).help_text: "help_text"
            }.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        CommentCreateFormTests.form.fields[
                            field
                        ].__dict__[value],
                        attr
                    )

    def test_create_comment_authrized_client(self):
        """Проверяем создание коментария авторизованным пользователем"""
        responce = self.authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={
                    "post_id": CommentCreateFormTests.post.id,
                },
            ),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), self.comment_count + 1)
        self.assertRedirects(
            responce,
            reverse(
                "posts:post_details",
                kwargs={"post_id": CommentCreateFormTests.post.id})
        )
        self.assertTrue(
            Comment.objects.filter(
                text=self.form_data["text"],
                author=CommentCreateFormTests.user,
            )
        )

    def test_create_comment_guest_client(self):
        """Проверяем невозможность создания коментария неавторизованным
        пользователем
        """
        response = self.guest_client.post(
            reverse(
                "posts:add_comment",
                kwargs={
                    "post_id": CommentCreateFormTests.post.id,
                },
            ),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), self.comment_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
