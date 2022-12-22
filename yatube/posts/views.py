from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Group

# Create your views here.

def index(request):
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')[:10]
    text = 'Последние обновления на сайте'
    context ={
        'title': text,
        'posts': posts,
    }
    return render(request, template, context)

def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-group')[:10]
    text = f'Записи сообщества {group.title}'
    context = {
        'title': text,
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)

def post_detail(request, slug):
    return HttpResponse(f'Post about {slug}')