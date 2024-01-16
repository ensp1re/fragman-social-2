from django.contrib import admin
from django.urls import path
from . import views
from posts.views import with_saves, with_posts


urlpatterns = [
    path('', views.index, name="index"),
    path("profile/<str:pk>", views.profile, name="profile"),
    path("notifications", views.notifications, name="notifications"),
    path("settings", views.settings, name="settings"),
    path("explore", views.explore, name="explore"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('follow', views.follow, name="follow"),
    path('unfollow', views.unfollow, name="unfollow"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("follow_back", views.follow_back, name="follow_back"),
    path("search", views.search, name="search"),
    path("follow_home", views.avax_follow_home, name="follow_home"),
    path("test", views.test, name="test"),
    path("create_send_message", views.create_send_message, name="create_snd"),
    path("messages/<str:id>", views.send_message, name="send_message"),
    path("messages", views.show_messages, name="show_msg"),
    # path("load_messages", views.load_message, name="load_message"),
    path("profile/<str:pk>/with_saves", with_saves, name="with_saves"),
    path("profile/<str:pk>/with_posts", with_posts, name="with_posts"),

]