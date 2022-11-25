from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse('Main page')

def group_posts(request):
    return HttpResponse('Posts group')

def post_detail(request, slug):
    return HttpResponse(f'Post about {slug}')