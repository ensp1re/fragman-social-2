from django.shortcuts import render, redirect
from main.models import Profile, Notification
from .models import Post, Comment, Saved
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string


@login_required(login_url='login')
def create_post(request):
    image_present = False
    if request.method == "POST":
        user_obj = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(username=user_obj)

        caption = request.POST.get("textPost")
        image = request.FILES.get("imgPost")

        if image:
            image_present = True

        if caption:
            if image:
                post = Post.objects.create(caption=caption, image=image, user_profile=profile, username=user_obj)
            else:
                post = Post.objects.create(caption=caption, user_profile=profile, username=user_obj)

            post.save()
            return redirect("/")

    context = {
        "image_present": image_present
    }

    return render(request, 'home.html', context)


@login_required(login_url='login')
def ajax_like(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        action = request.POST.get('action')
        profile = Profile.objects.get(username=request.user)

        post = get_object_or_404(Post, id=post_id)

        if action == 'like':
            post.liked_by.add(profile)
            if profile != post.user_profile:
                Notification.objects.create(sender=profile, receiver=post.user_profile,
                                            message=f"{profile.nickname.capitalize()} liked your <a class='notify-post' href='/post/status/{post.id}'>post</a>")
        elif action == 'unlike':
            post.liked_by.remove(profile)

        like_str = str()
        if post.get_number_of_likes() == 1:
            like_str = "1 like"
        elif post.get_number_of_likes() == 0:
            like_str = "No likes"
        else:
            like_str = f"{post.get_number_of_likes()} likes"

        return JsonResponse(
            {
                'status': 'success',
                "liked_by": post.get_number_of_likes(),
                "liked_post": like_str,
            }
        )
    else:
        return JsonResponse({'status': 'error'})


@login_required(login_url='login')
def comment(request):
    user = request.user
    profile = Profile.objects.filter(username=user).first()
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_id = request.POST.get("post_id_comment")
        caption = request.POST.get("commentField")

        post = Post.objects.filter(id=post_id).first()

        if post:
            comment = Comment.objects.create(post=post, author=profile, text=caption)
            if profile != post.user_profile:
                Notification.objects.create(sender=profile, receiver=post.user_profile,
                                            message=f"{profile.nickname.capitalize()} left a comment on <a class='notify-post' href='/post/status/{post.id}'>post</a>")
            comment.save()
            return JsonResponse({'status': 'success',
                                 'avatar': comment.author.avatar.url,
                                 'text': comment.text,
                                 'username_href': 'http://127.0.0.1:8000/profile/' + request.user.username,
                                 'username': request.user.username,
                                 'nickname': comment.author.nickname,
                                 })

        else:
            return JsonResponse({'status': 'error'})
    else:
        return JsonResponse({'status': 'error'})


@login_required(login_url='login')
def post_detail(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    my_profile = Profile.objects.get(username=request.user)

    if post.image:
        comments = post.comments.all()

        return render(request, 'kam.html',
                      {
                          "post_detail": post,
                          "comments": comments,
                          "post": post,
                          "my_profile": my_profile,

                      })
    else:
        comments = post.comments.all()
        return render(request, 'kam2.html',
                      {
                          "post_detail": post,
                          "comments": comments,
                          "my_profile": my_profile,
                          "post": post,
                      })


@login_required(login_url='login')
def save_post(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_id = request.POST.get("post_save_id")
        action = request.POST.get("action")
        profile = Profile.objects.get(username=request.user)

        post = get_object_or_404(Post, id=post_id)

        if post:
            if action == "save":
                saved, created = Saved.objects.get_or_create(post=post, user=profile)
                if created:
                    return JsonResponse({'status': 'success'})
            elif action == "unsave":
                saved = Saved.objects.get(post=post, user=profile)
                saved.delete()
                return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


def with_saves(request, pk):
    user_obj = User.objects.get(username=pk)
    my_profile = Profile.objects.get(username=user_obj)

    saves = Saved.objects.filter(user=my_profile).all()
    saved = [save.post for save in saves]

    return HttpResponse(render_to_string('with_saves.html',
                                         {
                                             'saved': saved,
                                             "my_profile": my_profile,
                                         }))


def with_posts(request, pk):
    user_obj = User.objects.get(username=pk)
    my_profile = Profile.objects.get(username=user_obj)

    posts = Post.objects.filter(username=user_obj)

    return HttpResponse(render_to_string('with_posts.html',
                                         {
                                             'posts': posts,
                                             "my_profile": my_profile,
                                         }))
