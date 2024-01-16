import uuid
from datetime import datetime
from django.db import models
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User
from main.models import Profile


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_by = models.ManyToManyField(Profile, default=None, related_name="likes", blank=True)
    caption = models.TextField(max_length=2000, blank=True)
    image = models.ImageField(upload_to="post_images", blank=True)
    created_at = models.DateTimeField(default=datetime.now)
    number_of_likes = models.IntegerField(default=0)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=1)

    def get_number_of_likes(self):
        return self.liked_by.all().count()

    def get_all_liked_profiles(self):
        return self.liked_by.all()

    # def get_date(self):
    #     current_time = datetime.now(timezone.utc)
    #     post_time = self.created_at.replace(tzinfo=timezone.utc)
    #
    #     time_difference = current_time - post_time
    #
    #     if time_difference < timedelta(minutes=60):
    #         minutes_passed = int(time_difference.total_seconds() / 60)
    #         return f"{minutes_passed} минут назад"
    #     elif time_difference < timedelta(hours=24):
    #         hours_passed = int(time_difference.total_seconds() / 3600)
    #         return f"{hours_passed} часов назад"
    #     elif post_time.year != current_time.year:
    #         return post_time.strftime("%b %d, %Y")
    #     else:
    #         return post_time.strftime("%b %d")

    def __str__(self):
        return f"{self.username}: {self.caption}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.author} commented: {self.post}"


class Saved(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_posts')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_saved')

    def get_all_posts(self):
        return self.post.all()

    def __str__(self):
        return f"{self.user} saved post => {self.post}"