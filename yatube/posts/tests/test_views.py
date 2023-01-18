import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..constants import POST_PER_PAGE
from ..models import Follow, Group, Post, User
from ..utils import get_author_name
from .constants import TEST_POST_COUNT


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.author = User.objects.create_user(username="TestAuthor")
        cls.user = User.objects.create_user(username="TestUser")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            description="Описание тестовой группы",
            slug="test"
        )

        cls.follow = Follow.objects.create(
            user=PostsPagesTests.user,
            author=PostsPagesTests.author
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x01\x00'
                b'\x01\x00\x00\x00\x00\x21\xf9\x04'
                b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
                b'\x00\x00\x01\x00\x01\x00\x00\x02'
                b'\x02\x4c\x01\x00\x3b'
            ),
            content_type='image/gif'
        )

        for i in range(TEST_POST_COUNT):
            cls.post = Post.objects.create(
                text=f"Текст тестового поста №: {i} для проверки",
                author=PostsPagesTests.author,
                group=PostsPagesTests.group,
                image=PostsPagesTests.uploaded,
            )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)
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
            reverse("posts:follow_index"): "posts/follow.html",
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
                    len(self.authorized_client.get(url).context["page_obj"]),
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
                obj.image: PostsPagesTests.post.image,
            }.items():
                with self.subTest(field=field):
                    self.assertEqual(field, value)

    def test_group_posts_page_correct_context(self):
        """"Проверяем корректность контекста для страницы группы постов"""
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
        """"Проверяем корректность контекста для страницы профиля автора"""
        for value, obj in {
            "author": PostsPagesTests.author,
            "author_full_name": get_author_name(PostsPagesTests.author),
            "count_posts": PostsPagesTests.author.posts.count(),
            "following": PostsPagesTests.user.follower.filter(
                author=PostsPagesTests.author).exists(),
        }.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.authorized_client.get(
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
        """"Проверяем корректность контекста для страниц создания и
        редактирования поста
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
                "image": forms.fields.ImageField,
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
            group=new_group,
            image=PostsPagesTests.uploaded,
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
        self.assertEqual(
            self.guest_client.get(reverse(
                "posts:post_details",
                kwargs={"post_id": new_post.id}
            )).context["post"],
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

    def test_show_comment(self):
        """Проверяем отображение созданного коментария на странице с
        информацией о посте
        """
        response = self.authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": PostsPagesTests.post.id},
            ),
            data={
                "text": "Коментарий к тестовому посту",
            },
            follow=True,
        )
        self.assertEqual(
            self.authorized_client.get(
                reverse(
                    "posts:post_details",
                    kwargs={"post_id": PostsPagesTests.post.id},
                )
            ).context["comments"][0].text,
            response.context["comments"][0].text
        )

    def test_show_image_on_post_details_page(self):
        """Проверяем передачу картинки в словаре контекста для страницы
        деталей поста
        """
        response = self.authorized_client.get(
            reverse(
                "posts:post_details",
                kwargs={"post_id": PostsPagesTests.post.id},
            )
        )
        self.assertEqual(
            response.context["post"].image,
            PostsPagesTests.post.image
        )

    def test_cache_index(self):
        post_for_deleting = Post.objects.create(
            text="Пост для проверки cache",
            author=PostsPagesTests.author,
        )
        first_response = self.authorized_client.get(reverse("posts:index"))
        post_for_deleting.delete()
        second_response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(first_response.content, second_response.content)
        cache.clear()
        third_response = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(first_response.content, third_response.content)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username="TestAuthor")
        cls.user = User.objects.create_user(username="TestUser")
        cls.new_user = User.objects.create_user(username="NewTestUser")

        cls.post = Post.objects.create(
            text="Пост для тестов подписок",
            author=FollowTests.author,
        )

        Follow.objects.create(
            user=FollowTests.user,
            author=FollowTests.author
        )

    def setUp(self):
        self.count_follow = Follow.objects.count()
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowTests.user)
        self.new_authorized_client = Client()
        self.new_authorized_client.force_login(FollowTests.new_user)

    def test_following(self):
        """Проверяем возможность подписаться на автора"""
        self.new_authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={
                    "username": FollowTests.author.username,
                }
            )
        )
        self.assertEqual(Follow.objects.count(), self.count_follow + 1)

    def test_unfollow(self):
        """Проверяем возможность отписаться от автора"""
        self.authorized_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={'username': FollowTests.author.username}
            ))
        self.assertEqual(Follow.objects.all().count(), self.count_follow - 1)

    def test_show_post_on_follow_page(self):
        """Проверяем появление поста на странице подписок у подписанного
        пользователя и отсутствие у неподписанного
        """
        self.assertIn(
            FollowTests.post,
            self.authorized_client.get(
                reverse("posts:follow_index")).context["page_obj"].object_list
        )
        self.assertNotIn(
            FollowTests.post,
            self.new_authorized_client.get(
                reverse("posts:follow_index")).context["page_obj"].object_list
        )
