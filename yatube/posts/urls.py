from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index),
    path('group/', views.group_posts, name='group_posts'),
    path('group_list.html', views.group_posts),
    path('group/<slug:slug>/', views.post_detail, name='group_slug'),
] 