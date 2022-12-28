from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..constants import POST_PER_PAGE
from ..models import Group, Post
from ..utils import get_author_name
from .constants import TEST_POST_COUNT

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username="TestUser")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            description="Описание тестовой группы",
            slug="test"
        )

        for i in range(TEST_POST_COUNT):
            cls.post = Post.objects.create(
                text=f"Текст тестового поста №: {i} для проверки",
                author=PostsPagesTests.author,
                group=PostsPagesTests.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="TestUserA")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostsPagesTests.author)

    def test_pages_correct_templates(self):
        """Проверяем работу namespace:name"""
        for reverse_name, template in {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:post_create"): "posts/post_create.html",
            reverse(
                "posts:profile",
                kwargs={"username": PostsPagesTests.author},
            ): "posts/profile.html",
            reverse(
                "posts:post_details",
                kwargs={"post_id": PostsPagesTests.post.id},
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": PostsPagesTests.post.id},
            ): "posts/post_create.html",
            reverse(
                "posts:group_list",
                kwargs={"slug": PostsPagesTests.group.slug},
            ): "posts/group_list.html",
        }.items():
            with self.subTest(template=template):
                self.assertTemplateUsed(
                    self.authorized_client_author.get(reverse_name),
                    template
                )

    def test_first_page_contains_ten_records(self):
        """Проверяем, что на первой странице количество отображаемых объектов
        равно POST_PER_PAGE
        """
        for url in [
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": PostsPagesTests.author}
            ),
            reverse(
                "posts:group_list",
                kwargs={"slug": PostsPagesTests.group.slug}
            ),
        ]:
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.guest_client.get(url).context["page_obj"]),
                    POST_PER_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверяем, что на второй странице количество отображаемых объектов
        равно TEST_POST_COUNT - POST_PER_PAGE
        """
        for url in [
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": PostsPagesTests.author}
            ),
            reverse(
                "posts:group_list",
                kwargs={"slug": PostsPagesTests.group.slug}
            ),
        ]:
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.guest_client.get(
                        url + "?page=2"
                    ).context["page_obj"]),
                    TEST_POST_COUNT - POST_PER_PAGE
                )

    def test_pages_with_pagination_correct_objects_fields(self):
        """Проверяем корректность полей объектов в post_obj для страниц
        с пагинацией
        """
        for url in [
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": PostsPagesTests.author}
            ),
            reverse(
                "posts:group_list",
                kwargs={"slug": PostsPagesTests.group.slug}
            ),
        ]:
            obj = self.guest_client.get(url).context["page_obj"][0]
            for field, value in {
                obj.text: f"Текст тестового поста №: {TEST_POST_COUNT - 1} "
                          "для проверки",
                obj.author: PostsPagesTests.author,
                obj.group: PostsPagesTests.group,
            }.items():
                with self.subTest(field=field):
                    self.assertEqual(field, value)

    def test_group_posts_page_correct_context(self):
        """"Проверяем корректность контеста для страницы группы постов"""
        self.assertEqual(
            self.guest_client.get(
                reverse(
                    "posts:group_list",
                    kwargs={"slug": PostsPagesTests.group.slug}
                )
            ).context["group"],
            PostsPagesTests.group
        )

    def test_profile_page_correct_context(self):
        """"Проверяем корректность контеста для страницы профиля автора"""
        for value, obj in {
            "author": PostsPagesTests.author,
            "author_full_name": get_author_name(PostsPagesTests.author),
            "count_posts": PostsPagesTests.author.posts.count(),
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.guest_client.get(
                        reverse(
                            "posts:profile",
                            kwargs={
                                "username":
                                PostsPagesTests.author.username
                            }
                        )
                    ).context[value],
                    obj
                )

    def test_create_and_edit_post_page_correct_context(self):
        """"Проверяем корректность контеста для страниц создания/редактирования
        поста
        """
        for url in (
            reverse("posts:post_create"),
            reverse("posts:post_edit", kwargs={
                "post_id": PostsPagesTests.post.id
            }),
        ):
            for value, expected in {
                "text": forms.fields.CharField,
                "group": forms.fields.ChoiceField,
            }.items():
                with self.subTest(value=value):
                    self.assertIsInstance(
                        self.authorized_client_author.get(url).context[
                            "form"
                        ].fields[value],
                        expected
                    )

    def test_edit_post_page_correct_form_in_context(self):
        """Проверяем корректность содержимого формы при редактировании поста"""
        self.assertEqual(
            self.authorized_client_author.get(
                reverse(
                    "posts:post_edit",
                    kwargs={"post_id": PostsPagesTests.post.id}
                )
            ).context["form"].instance,
            PostsPagesTests.post
        )

    def test_show_new_post_on_pages(self):
        """Проверяем отображение нового поста на страницах"""
        new_group = Group.objects.create(
            title="Группа2",
            slug="test2",
            description="Группа для проверки"
        )
        new_post = Post.objects.create(
            text="Текст нового поста",
            author=PostsPagesTests.author,
            group=new_group
        )
        for url in (
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": PostsPagesTests.author.username}
            ),
            reverse(
                "posts:group_list",
                kwargs={"slug": new_group.slug}
            ),
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).context["page_obj"][0],
                    new_post
                )
        self.assertIsNot(
            self.guest_client.get(
                reverse(
                    "posts:group_list",
                    kwargs={"slug": PostsPagesTests.group.slug}
                )
            ).context["page_obj"][0],
            new_post
        )
