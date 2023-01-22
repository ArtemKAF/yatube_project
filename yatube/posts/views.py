from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .constants import CACHE_INDEX, POST_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import create_pagination, get_author_name


@cache_page(CACHE_INDEX, key_prefix="page_index")
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
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user)
    context = {
        "form": form,
        "title": "Добавить запись",
        "is_edit": False,
    }
    return render(request, "posts/post_create.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:profile", post.author)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
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
    following = False
    if request.user.is_authenticated:
        if request.user.follower.filter(author=author).exists():
            following = True
    context = {
        "page_obj": create_pagination(
            author.posts.select_related("group"),
            POST_PER_PAGE,
            request.GET.get("page")
        ),
        "author": author,
        "author_full_name": get_author_name(author),
        "count_posts": author.posts.count(),
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        "post": post,
        "count_posts": post.author.posts.count(),
        "author_full_name": get_author_name(post.author),
        "form": CommentForm(),
        "comments": post.comments.all(),
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_details', post_id)


@login_required
def follow_index(request):
    return render(
        request,
        'posts/follow.html',
        context={
            "page_obj": create_pagination(
                Post.objects.filter(
                    author__following__user=request.user,
                ),
                POST_PER_PAGE,
                request.GET.get("page")
            ),
        },
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    is_follower = user.follower.filter(author=author).exists()
    if user != author and not is_follower:
        Follow.objects.create(user=user, author=author)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    is_follower = user.follower.filter(author=author).exists()
    if user != author and is_follower:
        temp = Follow.objects.filter(user=user, author=author)
        temp.delete()
    return redirect("posts:profile", username)
