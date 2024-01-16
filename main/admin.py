from django.contrib import admin
from .models import Profile, Relationship, MessageRelation, Messages, Notification



admin.site.register(Profile)
admin.site.register(Relationship)
admin.site.register(MessageRelation)
admin.site.register(Messages)
admin.site.register(Notification)
