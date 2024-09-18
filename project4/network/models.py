from typing import Any
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    following_list = models.ManyToManyField(
        "User", related_name="followers", blank=True
    )


class Post(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="posts")
    text = models.CharField(max_length=200, blank=False, null=False)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    timestamp = models.DateTimeField(auto_now_add=True)

    def serializer(self):
        return {
            "id": self.id,
            "user": self.user,
            "text": self.text,
            "likes": self.likes.all(),
            "timestamp": self.timestamp,
        }


class Comment(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="user_comments")
    text = models.CharField(max_length=200, blank=False, null=False)
    post = models.ForeignKey(Post, models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(auto_now_add=True)
