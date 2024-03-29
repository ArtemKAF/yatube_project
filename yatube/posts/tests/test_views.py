import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..constants import POST_PER_PAGE
from ..forms import PostForm
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

        picture = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00"
            b"\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )

        cls.list_posts = []

        for i in range(TEST_POST_COUNT - 1):
            cls.list_posts.append(
                Post(
                    text=f"Текст тестового поста №: {i} для проверки",
                    author=PostsPagesTests.author,
                    group=PostsPagesTests.group,
                    image=SimpleUploadedFile(
                        name=f"small_{i}.gif",
                        content=picture,
                        content_type="image/gif"
                    ),
                )
            )
        Post.objects.bulk_create(cls.list_posts)

        cls.post = Post.objects.create(
            text="Текст тестового поста для проверки",
            author=PostsPagesTests.author,
            group=PostsPagesTests.group,
            image=SimpleUploadedFile(
                name="small.gif",
                content=picture,
                content_type="image/gif"
            ),
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
        for url, template in (
            (reverse("posts:index"), "posts/index.html"),
            (reverse("posts:post_create"), "posts/post_create.html"),
            (reverse(
                "posts:profile", args=(PostsPagesTests.author.username,),
            ), "posts/profile.html"),
            (reverse(
                "posts:post_details", args=(PostsPagesTests.post.id,),
            ), "posts/post_detail.html"),
            (reverse(
                "posts:post_edit", args=(PostsPagesTests.post.id,),
            ), "posts/post_create.html"),
            (reverse(
                "posts:group_list", args=(PostsPagesTests.group.slug,),
            ), "posts/group_list.html"),
            (reverse("posts:follow_index"), "posts/follow.html"),
        ):
            with self.subTest(template=template):
                self.assertTemplateUsed(
                    self.authorized_client_author.get(url),
                    template
                )

    def test_first_page_contains_ten_records(self):
        """Проверяем, что на первой странице количество отображаемых объектов
        равно POST_PER_PAGE
        """
        for url in (
            reverse("posts:index"),
            reverse("posts:profile", args=(PostsPagesTests.author,)),
            reverse("posts:group_list", args=(PostsPagesTests.group.slug,)),
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.authorized_client.get(url).context["page_obj"]),
                    POST_PER_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверяем, что на второй странице количество отображаемых объектов
        равно TEST_POST_COUNT - POST_PER_PAGE
        """
        for url in (
            reverse("posts:index"),
            reverse("posts:profile", args=(PostsPagesTests.author,)),
            reverse("posts:group_list", args=(PostsPagesTests.group.slug,)),
        ):
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
        for url in (
            reverse("posts:index"),
            reverse("posts:profile", args=(PostsPagesTests.author,)),
            reverse("posts:group_list", args=(PostsPagesTests.group.slug,)),
        ):
            obj = self.guest_client.get(url).context["page_obj"][0]
            for field, value in (
                (obj.text, "Текст тестового поста для проверки"),
                (obj.author, PostsPagesTests.author),
                (obj.group, PostsPagesTests.group),
                (obj.image, PostsPagesTests.post.image),
            ):
                with self.subTest(field=field):
                    self.assertEqual(field, value)

    def test_group_posts_page_correct_context(self):
        """"Проверяем корректность контекста для страницы группы постов"""
        self.assertEqual(
            self.guest_client.get(
                reverse(
                    "posts:group_list", args=(PostsPagesTests.group.slug,)
                )
            ).context["group"],
            PostsPagesTests.group
        )

    def test_profile_page_correct_context(self):
        """"Проверяем корректность контекста для страницы профиля автора"""
        for value, obj in (
            ("author", PostsPagesTests.author),
            ("author_full_name", get_author_name(PostsPagesTests.author)),
            ("count_posts", PostsPagesTests.author.posts.count()),
            ("following", PostsPagesTests.user.follower.filter(
                author=PostsPagesTests.author).exists()),
        ):
            with self.subTest(value=value):
                self.assertEqual(
                    self.authorized_client.get(
                        reverse(
                            "posts:profile",
                            args=(PostsPagesTests.author.username,)
                        )
                    ).context[value],
                    obj
                )

    def test_create_and_edit_post_page_correct_context(self):
        """Проверяем корректность контекста страницы создания/редактирования
        поста
        """
        urls = (
            ("posts:post_create", None, False),
            ("posts:post_edit", (PostsPagesTests.post.id,), True),
        )
        for name, args, is_edit_value in urls:
            with self.subTest(name=name):
                response = self.authorized_client_author.get(
                    reverse(name, args=args)
                )

                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], PostForm)

                self.assertIn("is_edit", response.context)
                is_edit = response.context["is_edit"]
                self.assertIsInstance(is_edit, bool)
                self.assertEqual(is_edit, is_edit_value)

    def test_edit_post_page_correct_form_in_context(self):
        """Проверяем корректность содержимого формы при редактировании поста"""
        self.assertEqual(
            self.authorized_client_author.get(
                reverse(
                    "posts:post_edit",
                    args=(PostsPagesTests.post.id,)
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
        )
        for url in (
            reverse("posts:index"),
            reverse(
                "posts:profile", args=(PostsPagesTests.author.username,)
            ),
            reverse("posts:group_list", args=(new_group.slug,)),
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).context["page_obj"][0],
                    new_post
                )
        self.assertEqual(
            self.guest_client.get(
                reverse("posts:post_details", args=(new_post.id,))
            ).context["post"],
            new_post
        )
        self.assertIsNot(
            self.guest_client.get(
                reverse("posts:group_list", args=(PostsPagesTests.group.slug,))
            ).context["page_obj"][0],
            new_post
        )

    def test_show_comment(self):
        """Проверяем отображение созданного коментария на странице с
        информацией о посте
        """
        response = self.authorized_client.post(
            reverse(
                "posts:add_comment", args=(PostsPagesTests.post.id,)
            ),
            data={"text": "Коментарий к тестовому посту"},
            follow=True,
        )
        self.assertEqual(
            self.authorized_client.get(
                reverse(
                    "posts:post_details", args=(PostsPagesTests.post.id,),
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
                "posts:post_details", args=(PostsPagesTests.post.id,)
            )
        )
        self.assertEqual(
            response.context["post"].image,
            PostsPagesTests.post.image
        )

    def test_cache_index(self):
        """Проверяем работу кэша на странице index"""
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
                "posts:profile_follow", args=(FollowTests.author.username,)
            )
        )
        self.assertEqual(Follow.objects.count(), self.count_follow + 1)

    def test_unfollow(self):
        """Проверяем возможность отписаться от автора"""
        self.authorized_client.get(
            reverse(
                "posts:profile_unfollow", args=(FollowTests.author.username,)
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
