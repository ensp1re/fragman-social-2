import this
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from .utils import get_random_code, get_random_id_message




class Profile(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    avatar = models.ImageField(default="photo_2021-10-16_13-01-08.jpg", upload_to='avatars/')
    bio = models.TextField(max_length=2000, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_friends(self):
        return self.friends.all()


    def get_friend_number(self):
        return self.friends.all().count()

    def __str__(self):
        return self.username.username + " " + self.created.strftime("%Y.%m.%d %H:%M")


class RelationShipManager(models.Manager):

    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=reveiver, status='send')
        return qs

    def followers(self, user_profile):
        num = Relationship.objects.filter(receiver=user_profile, status="send").count()
        result = int()
        if Relationship.objects.filter(receiver=user_profile, status="accepted").exists():
            num_followed = Relationship.objects.filter(receiver=user_profile, status="accepted").count()
            if num == 0:
                num += 1
            result = num * num_followed
        return result

    def following(self, user_profile):
        num = Relationship.objects.filter(sender=user_profile, status="send").count()
        result = int()
        if  Relationship.objects.filter(sender=user_profile, status="accepted").exists():
            num_followed = Relationship.objects.filter(sender=user_profile, status="accepted").count()
            if num == 0:
                num += 1
            result = num * n8um_followed
        return result



STATUC_CHOICES = {
    ("send", "send"),
    ("accepted", "accepted")
}

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receiver")
    status = models.CharField(max_length=8, choices=STATUC_CHOICES)
    updated = models.DateTimeField(auto_now_add=True)

    objects = RelationShipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"


class MessageManager(models.Manager):

    def get_last_message(self, rel_message_id):
        rel_mes_obj = MessageRelation.objects.filter(id=rel_message_id).first()
        messages_obj = Messages.objects.filter(MSGRelation=rel_mes_obj).last()
        return last_message





class MessageRelation(models.Model):
    id = models.CharField(primary_key=True, default=get_random_id_message, max_length=50, unique=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender_msgr')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver_msgr')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} contacted with {self.receiver}"


class Messages(models.Model):
    MSGRelation = models.ForeignKey(MessageRelation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender_m')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver_m')
    content = models.TextField(blank=True, max_length=2000)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    objects = MessageManager()


    def __str__(self):
        return f"{self.sender} sent message to {self.receiver}"



class Notification(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="notif_sender")
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="notif_receiver")
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} {self.message} - {self.receiver}"

