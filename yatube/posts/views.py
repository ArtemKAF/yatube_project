from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Group

# Create your views here.

def index(request):
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')[:10]
    context ={
        'text': 'Main Page',
        'posts': posts,
    }
    return render(request, template, context)

def group_posts(request, slug):
    template = 'posts/group_list.html'
    text = 'Posts group'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'text': text,
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)

def post_detail(request, slug):
    return HttpResponse(f'Post about {slug}')