from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('create_post', views.create_post, name="create_post"),
    path("like", views.ajax_like, name="like"),
    path("comment", views.comment, name="comment"),
    path("save_post", views.save_post, name="save_post"),
    path("status/<str:post_id>", views.post_detail, name="post_detail"),
]