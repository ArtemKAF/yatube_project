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
            Post.objects.all(),
            POST_PER_PAGE,
            request.GET.get("page")
        ),
    }
    return render(request, "posts/index.html", context)


@login_required
def post_create(request):
    template = "posts/post_create.html"
    title = "Добавить запись"
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", request.user)
        context = {
            "form": form,
            "is_edit": False,
            "title": title,
        }
        return render(request, template, context)
    else:
        form = PostForm()
        context = {
            "form": form,
            "is_edit": False,
            "title": title,
        }
        return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        template = "posts/post_create.html"
        title = "Редактировать запись"
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post.text = form.cleaned_data["text"]
                post.group = form.cleaned_data["group"]
                post.save()
                return redirect("posts:post_details", post.id)
            context = {
                "form": form,
                "is_edit": True,
                "title": title,
            }
            return render(request, template, context)
        else:
            form = PostForm(instance=post)
            context = {
                "form": form,
                "is_edit": True,
                "title": title,
            }
            return render(request, template, context)
    return redirect("posts:profile", post.author)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        "group": group,
        "page_obj": create_pagination(
            group.groups.all(),
            POST_PER_PAGE,
            request.GET.get("page")
        ),
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {
        "page_obj": create_pagination(
            Post.objects.filter(author=author),
            POST_PER_PAGE,
            request.GET.get("page")
        ),
        "author": author,  # Только ради тестов в pytest
        "author_full_name": get_author_name(author),
        "count_posts": Post.objects.filter(author=author).count(),
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        "post": post,
        "count_posts": Post.objects.filter(author=post.author).count(),
        "author_full_name": get_author_name(post.author),
    }
    return render(request, "posts/post_detail.html", context)
