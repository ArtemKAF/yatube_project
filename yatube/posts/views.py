from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    template = 'posts/index.html'
    text = 'This is main page'
    context ={
        'text': text,
    }
    return render(request, template, context)

def group_posts(request):
    template = 'posts/group_list.html'
    text = 'Here will be information about the Yatube project groups'
    context = {
        'text': text,
    }
    return render(request, template, context)

def post_detail(request, slug):
    return HttpResponse(f'Post about {slug}')