from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .constants import POST_PER_PAGE
from .forms import PostForm
from .models import Group, Post
from .utils import create_pagination, get_author_name

User = get_user_model()


def index(request):
    context = {
        "page_obj": create_pagination(
            Post.objects.select_related("group", "author"),
            POST_PER_PAGE,
            request.GET.get("page")
        ),
    }
    return render(request, "posts/index.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user)
    context = {
        "form": form,
        "title": "Добавить запись",
    }
    return render(request, "posts/post_create.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:profile", post.author)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_details", post.id)
    context = {
        "form": form,
        "is_edit": True,
        "title": "Редактировать запись",
    }
    return render(request, "posts/post_create.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        "group": group,
        "page_obj": create_pagination(
            group.posts.select_related("author"),
            POST_PER_PAGE,
            request.GET.get("page")
        ),
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {
        "page_obj": create_pagination(
            author.posts.select_related("group"),
            POST_PER_PAGE,
            request.GET.get("page")
        ),
        "author": author,  # Только ради тестов в pytest
        "author_full_name": get_author_name(author),
        "count_posts": author.posts.count(),
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        "post": post,
        "count_posts": post.author.posts.count(),
        "author_full_name": get_author_name(post.author),
    }
    return render(request, "posts/post_detail.html", context)
