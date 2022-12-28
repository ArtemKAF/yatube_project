from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username="TestUser")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            description="Описание тестовой группы",
            slug="test",
        )

        cls.post = Post.objects.create(
            text="Текст тестового поста для проверки",
            author=PostsUrlsTests.author,
            group=PostsUrlsTests.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="TestUserA")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostsUrlsTests.author)

    def test_urls_at_exists_desired_location(self):
        """Проверяем доступность адресов неавторизованному пользователю"""
        for url in [
            "/",
            "/profile/TestUserA/",
            f"/posts/{PostsUrlsTests.post.id}/",
            "/group/test/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_urls_at_desired_location_authorized(self):
        """Проверяем доступность адресов для авторизованного пользователя"""
        for url in [
            "/",
            "/create/",
            "/profile/TestUserA/",
            f"/posts/{PostsUrlsTests.post.id}/",
            "/group/test/",
        ]:
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
        self.assertRedirects(
            self.authorized_client.get(
                f"/posts/{PostsUrlsTests.post.id}/edit/",
                follow=True
            ),
            f"/profile/{PostsUrlsTests.post.author}/"
        )

    def test_uses_templates(self):
        """Проверяем используемые шаблоны для адресов в urls.py"""
        for url, template in {
            "/": "posts/index.html",
            "/create/": "posts/post_create.html",
            f"/profile/{PostsUrlsTests.author}/": "posts/profile.html",
            f"/posts/{PostsUrlsTests.post.id}/": "posts/post_detail.html",
            f"/posts/{PostsUrlsTests.post.id}/edit/": "posts/post_create.html",
            f"/group/{PostsUrlsTests.group.slug}/": "posts/group_list.html",
        }.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client_author.get(url),
                    template
                )
