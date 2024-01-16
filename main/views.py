import random
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from posts.models import Post
from django.shortcuts import get_object_or_404
from itertools import chain
from random import shuffle
from django.db.models import Q
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User, auth
from .models import Profile, Relationship, MessageRelation, Messages, Notification
from posts.models import Saved

from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def index(request):
    user = request.user

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(username=user_object)

    posts = Post.objects.all()

    user_following = Relationship.objects.filter(
        ((Q(sender=user_profile) & Q(status="send")) | (Q(sender=user_profile) & Q(status="accepted"))))
    # new users suggestion

    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.receiver.username)
        user_following_all.append(user_list)

    new_user_suggestion = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [x for x in list(new_user_suggestion) if x not in list(current_user)]
    random.shuffle(final_suggestion_list)

    username_profile_list = []

    for username_obj in final_suggestion_list:
        username_profile_list.append(Profile.objects.filter(username=username_obj))

    suggestion_username_profiles = list(chain(*username_profile_list))
    print(suggestion_username_profiles)

    all_notification = Notification.objects.filter(receiver=user_profile).all()
    count_of_not_read = list()
    for notification in all_notification:
        is_read = notification.is_read
        if not is_read:
            count_of_not_read.append(is_read)

    saved_posts = Saved.objects.filter(user=user_profile).all()
    my_saved_posts = [save.post for save in saved_posts]

    return render(request, "home.html", {
        "user": request.user,
        "posts": posts,
        "saved_posts": my_saved_posts,
        "profile": user_profile,
        "suggestion": suggestion_username_profiles[:4],
        "num_of_notification": len(count_of_not_read)
    })


@login_required(login_url='login')
def profile(request, pk):
    user = request.user
    return render(request, "profile.html", {
        "user": user
    })


@login_required(login_url='login')
def notifications(request):
    user = request.user
    my_profile = Profile.objects.filter(username=user).first()
    all_notifications = Notification.objects.filter(receiver=my_profile).all()

    for notification in all_notifications:
        notification.is_read = True
        notification.save()

    return render(request, "notifications.html", {
        "user": user,
        "my_profile": my_profile,
        "notifications": all_notifications,

    })


@login_required(login_url='login')
def explore(request):
    user = request.user
    user_obj = User.objects.get(username=user.username)
    my_profile = Profile.objects.get(username=user_obj)

    return render(request, 'explore.html', {
        "my_profile": my_profile,
        "user": user
    })


@login_required(login_url="login")
def search(request):
    search_query = request.GET.get("q", "")

    user_object = request.user
    my_profile = Profile.objects.get(username=user_object)

    username_object = User.objects.filter(username__icontains=search_query)

    if username_object:
        username_profiles = []
        username_profile_list = []

        for users in username_object:
            username_profiles.append(Profile.objects.filter(username=users))

        username_profile_list = list(chain(*username_profiles))
        return render(request, "find_people.html", {
            "is_users": True,
            "users": username_profile_list,
            "my_profile": my_profile,
            'is_me': True if my_profile in username_profile_list else False,
            "user": user_object

        })
    else:
        return render(request, "find_people.html", {
            "is_users": False,
            "my_profile": my_profile,
            "user": user_object

        })


@login_required(login_url='login')
def settings(request):
    user = request.user
    user_obj = User.objects.get(username=user.username)
    profile = Profile.objects.get(username=user_obj)

    return render(request, 'settings.html', {
        "my_profile": profile,
        "user": user,
    })


def edit_profile(request):
    user = request.user.username
    user_obj = User.objects.get(username=user)
    profile = Profile.objects.get(username=user_obj)

    if request.method == "POST":
        nickname = request.POST.get("nickname")
        avatar = request.FILES.get("avatar")
        username = request.POST.get("username")
        bio = request.POST.get("bio")

        if nickname:
            profile.nickname = nickname
        if avatar:
            profile.avatar = avatar
        if bio:
            #  add <p></p> instead of "\n"
            bio_split = bio.split("\n")
            new_bio = "\n".join(["<p></p>" if not text.split() else text for text in bio_split])

            profile.bio = mark_safe(bio)
        if username:
            if User.objects.filter(username=username).exists():
                messages.info(request, f"{username} has already taken!")
                return redirect("settings")
            else:
                user_obj.username = username

        profile.save()
        user_obj.save()
        return redirect("settings")
    else:
        messages.info(request, "Error, try again!")
        return redirect("settings")
    return redirect("settings")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmpassword")

        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.info(request, "This email has already registered!")
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "This username was taken!")
                return redirect('register')
            else:

                # Create user
                user = User.objects.create_user(username=username, email=email, password=confirm_password)
                user.save()

                # Login user
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # Create profile for user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(username=user_model, nickname=username)
                new_profile.save()
                return redirect("index")
        else:
            messages.info(request, "Passwords don't match")
            return redirect('register')
    else:
        return render(request, "sign_up.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, "Error!")
            return redirect("login")
    else:
        return render(request, "sign-in.html")


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required(login_url='login')
def profile(requwst, pk):
    # user pk
    user_obj = User.objects.get(username=pk)
    profile = Profile.objects.get(username=user_obj)

    # user posts

    posts = Post.objects.filter(username=user_obj)

    # me
    user_obj_me = User.objects.get(username=requwst.user.username)
    my_profile = Profile.objects.get(username=user_obj_me)

    is_following = Relationship.objects.filter(sender=my_profile, receiver=profile, status="send").exists()
    is_follower = Relationship.objects.filter(sender=profile, receiver=my_profile, status="send").exists()
    is_friends = Relationship.objects.filter(
        Q(sender=profile, receiver=my_profile, status="accepted") | Q(sender=my_profile, receiver=profile,
                                                                      status="accepted")
    ).exists()

    # get following and followers
    num_followers = Relationship.objects.filter(receiver=profile, status="send").count()
    result_followers = int()
    num_followed_followers = Relationship.objects.filter(receiver=profile, status="accepted").count()

    num_following = Relationship.objects.filter(sender=profile, status="send").count()
    result_following = int()
    num_followed_following = Relationship.objects.filter(sender=profile, status="accepted").count()

    result_following = num_following + num_followed_following + num_followed_followers

    result_followers = num_followed_followers + num_followers + num_followed_following

    context = {
        "profile": profile,
        "my_profile": my_profile,
        "posts": posts,
        "number_of_posts": len(posts),
        "is_following": is_following,
        "following": result_following,
        "followers": result_followers,
        "is_follower": is_follower,
        "is_friends": is_friends,
        "user": pk,
    }

    return render(requwst, "profile.html", context)


@login_required(login_url='login')
def follow(request):
    if request.method == "POST":

        user = request.user
        pk = request.POST.get("receiver")
        pk_obj = User.objects.get(username=pk)
        sender = Profile.objects.get(username=user)
        receiver = Profile.objects.get(username=pk_obj)

        if not Relationship.objects.filter(sender=sender, receiver=receiver, status="send").exists():
            rel = Relationship.objects.create(sender=sender, receiver=receiver, status="send")
            Notification.objects.create(sender=sender, receiver=receiver,
                                        message=f"{sender.nickname.capitalize()} follows you")

        return redirect(f"profile/{pk}")
    return redirect('/')


@login_required(login_url='login')
def unfollow(request):
    if request.method == "POST":
        user = request.user
        pk = request.POST.get("receiver")
        pk_obj = User.objects.get(username=pk)

        sender = Profile.objects.get(username=user)
        receiver = Profile.objects.get(username=pk_obj)

        rel = Relationship.objects.filter(Q(sender=sender, receiver=receiver, status="accepted") | Q(sender=receiver, receiver=sender, status="accepted"))
        if rel.exists():
            rel.update(status="send")
            return redirect(f"profile/{pk}")
        else:
            Relationship.objects.filter(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
            ).delete()
            return redirect(f"profile/{pk}")
    return redirect('/')


@login_required(login_url='login')
def follow_back(request):
    if request.method == "POST":
        user = request.user
        pk = request.POST.get("receiver")
        pk_obj = User.objects.get(username=pk)

        sender = Profile.objects.get(username=user)
        receiver = Profile.objects.get(username=pk_obj)

        rel = get_object_or_404(Relationship, sender=receiver, receiver=sender)
        if rel.status == "send":
            rel.status = "accepted"
            rel.save()

        return redirect(f"profile/{pk}")
    return redirect('/')


@login_required(login_url='login')
def avax_follow_home(request):
    # ajax method and "POST"
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        user = request.user
        pk_obj = User.objects.get(username=receiver_username)

        sender = Profile.objects.get(username=user)
        receiver = Profile.objects.get(username=pk_obj)
        action = request.POST.get("action")

        if action == "follow":
            if not Relationship.objects.filter(sender=sender, receiver=receiver, status="send").exists():
                rel = Relationship.objects.create(sender=sender, receiver=receiver, status="send")
                Notification.objects.create(sender=sender, receiver=receiver,
                                            message=f"{sender.nickname.capitalize()} follows you")
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse({
                "status": "error"
            })
    elif action == "unfollow":
        if Relationship.objects.filter(sender=sender, receiver=receiver, status="send").exists():
            Relationship.objects.filter(sender=sender, receiver=receiver, status="send").first().delete()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse({
                "status": "error"
            })
    return JsonResponse({
        "status": "error"
    })


def test(request):
    return render(request, 'test.html')


def create_send_message(request):
    sender = Profile.objects.filter(username=request.user).first()
    if request.method == "POST":
        get_receiver = request.POST.get("profile-receiver")
        receiver_obj = User.objects.get(username=get_receiver)
        receiver = Profile.objects.filter(username=receiver_obj).first()

        if not MessageRelation.objects.filter(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)).exists():
            message = MessageRelation.objects.create(sender=sender, receiver=receiver)
            message.save()
            return redirect("send_message", id=message.id)
        else:
            message = MessageRelation.objects.filter(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)).first()
            return redirect("send_message", id=message.id)
    return render(request, 'profile.html')


def send_message(request, id):
    sender = Profile.objects.filter(username=request.user).first()

    message_relation = MessageRelation.objects.filter(id=id).first()
    all_messages_for_id = message_relation.messages.all()
    receiver = message_relation.receiver

    last_message = message_relation.messages.last()
    last_message.is_read = True
    last_message.save()

    if request.method == "POST":
        content = request.POST.get("message")
        Messages.objects.create(content=content, sender=sender, receiver=receiver, MSGRelation=message_relation)
        return redirect("send_message", id=id)

    return render(request, "chatting.html", {
        "id": id,
        "my_profile": sender,
        "receiver": receiver,
        "messages": all_messages_for_id,
    })


def show_messages(request):
    sender = Profile.objects.get(username=request.user)

    all_rel_messages = MessageRelation.objects.all()

    return render(request, 'messages.html', {
        "my_profile": sender,
        'messages': all_rel_messages,
        "user": request.user
    })

# def load_message(request):
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         rel_id = request.GET.get("rel_id")
#         msg_count_id = request.GET.get("last_id_message")
#
#         rel_obj = MessageRelation.objects.get(id=rel_id)
#         all_messages = rel_obj.messages.all()
#
#         message = all_messages[msg_count_id:msg_count_id+7]
#
#         data = [{
#             "sender" : message.sender,
#             "receiver" : message.receiver,
#             "content" : message.content
#         } for message in messages]
#
#
#         return JsonResponse({
#             "data" : data
#         })
