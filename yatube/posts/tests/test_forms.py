from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username="TestUser")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            description="Группа для тестов",
            slug="test"
        )

        cls.post = Post.objects.create(
            text="Текст поста для проверки",
            author=PostsCreateFormTests.author,
            group=PostsCreateFormTests.group
        )

        cls.form = PostForm()

    def setUp(self):
        self.posts_count = Post.objects.count()
        self.form_data = {
            "text": "Пост для теста формы",
            "group": PostsCreateFormTests.group.pk
        }
        self.guest_client = Client()
        self.user = User.objects.create_user(username="TestUserA")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostsCreateFormTests.author)

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

    def test_create_post(self):
        """Проверяем создание поста"""
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
                kwargs={"username": self.user.username})
        )

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
        self.assertEqual(
            Post.objects.get(id=PostsCreateFormTests.post.id).text,
            self.form_data["text"]
        )
