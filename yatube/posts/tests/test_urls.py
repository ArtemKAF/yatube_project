from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Comment, Follow, Group, Post, User


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username="TestAuthor")
        cls.user = User.objects.create_user(username="TestUser")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            description="Описание тестовой группы",
            slug="test",
        )

        cls.post = Post.objects.create(
            text="Текст тестового поста для проверки",
            author=cls.author,
            group=cls.group,
        )

        Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text="Текст коментария",
        )

        Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsUrlsTests.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostsUrlsTests.author)

    def test_urls_at_exists_desired_location(self):
        """Проверяем доступность адресов неавторизованному пользователю"""
        for url in (
            "/",
            f"/profile/{PostsUrlsTests.author.username}/",
            f"/posts/{PostsUrlsTests.post.id}/",
            f"/group/{PostsUrlsTests.group.slug}/",
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_urls_at_desired_location_authorized(self):
        """Проверяем доступность адресов для авторизованного пользователя"""
        for url in (
            "/",
            "/create/",
            f"/profile/{PostsUrlsTests.author.username}/",
            f"/posts/{PostsUrlsTests.post.id}/",
            f"/group/{PostsUrlsTests.group.slug}/",
            "/follow/",
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_access_edit_post_author(self):
        """Проверяем доступность редактирования поста автором"""
        self.assertEqual(
            self.authorized_client_author.get(
                f"/posts/{PostsUrlsTests.post.id}/edit/"
            ).status_code,
            HTTPStatus.OK
        )

    def test_access_not_exist_page(self):
        """Проверяем, что при обращении к несуществующей странице возвращается
        ошибка 404
        """
        self.assertEqual(
            self.guest_client.get(
                "/not_exist_page/"
            ).status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_urls_redirect_anonymous(self):
        """Проверяем адреса перенаправления неавторизованного пользователя"""
        for url, redirect_url in {
            "/create/": "/auth/login/?next=/create/",
            f"/posts/{PostsUrlsTests.post.id}/edit/":
            f"/auth/login/?next=/posts/{PostsUrlsTests.post.id}/edit/",
            f"/posts/{PostsUrlsTests.post.id}/comment/":
            f"/auth/login/?next=/posts/{PostsUrlsTests.post.id}/comment/",
            f"/profile/{PostsUrlsTests.author.username}/follow/":
            f"/auth/login/?next=/profile/{PostsUrlsTests.author.username}"
            "/follow/",
            f"/profile/{PostsUrlsTests.author.username}/unfollow/":
            f"/auth/login/?next=/profile/{PostsUrlsTests.author.username}"
            "/unfollow/",
        }.items():
            with self.subTest(url=url):
                self.assertRedirects(
                    self.guest_client.get(url, follow=True),
                    redirect_url
                )

    def test_urls_redirect_authorized_not_author_post(self):
        """Проверяем перенаправление авторизованного пользователя на страницу
        профиля автора поста, если пользователь не автор
        """
        for url, redirects in {
            f"/posts/{PostsUrlsTests.post.id}/edit/":
            f"/profile/{PostsUrlsTests.post.author}/",
            f"/posts/{PostsUrlsTests.post.id}/comment/":
            f"/posts/{PostsUrlsTests.post.id}/",
            f"/profile/{PostsUrlsTests.author.username}/follow/":
            f"/profile/{PostsUrlsTests.author.username}/",
            f"/profile/{PostsUrlsTests.author.username}/unfollow/":
            f"/profile/{PostsUrlsTests.author.username}/",
        }.items():
            with self.subTest(url=url):
                self.assertRedirects(
                    self.authorized_client.get(
                        url,
                        follow=True
                    ),
                    redirects
                )

    def test_uses_templates(self):
        """Проверяем используемые шаблоны для адресов в urls.py"""
        cache.clear()
        for url, template in {
            "/": "posts/index.html",
            "/create/": "posts/post_create.html",
            f"/profile/{PostsUrlsTests.author.username}/":
            "posts/profile.html",
            f"/posts/{PostsUrlsTests.post.id}/": "posts/post_detail.html",
            f"/posts/{PostsUrlsTests.post.id}/edit/": "posts/post_create.html",
            f"/group/{PostsUrlsTests.group.slug}/": "posts/group_list.html",
            "/not_exist_page/": "core/404.html",
        }.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client_author.get(url),
                    template
                )
