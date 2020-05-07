from django.db import models
from django.contrib.auth.models import AbstractUser


class StarnaviUser(AbstractUser):
    first_name = models.CharField(max_length=15, verbose_name='first name')

    def __str__(self):
        return self.username


class Post(models.Model):
    post_text = models.CharField(max_length=1000, verbose_name='post')
    post_published = models.DateTimeField(auto_now_add=True, verbose_name='post date')
    post_user = models.ForeignKey(StarnaviUser, related_name='posts', on_delete=models.CASCADE, verbose_name='Author post')


class Like(models.Model):
    like_user = models.ForeignKey(StarnaviUser, related_name='like_user', on_delete=models.CASCADE)
    like_post = models.ForeignKey(Post, related_name='like_post', on_delete=models.CASCADE)
    like = models.SmallIntegerField(default=0)
    like_published = models.DateField(format('%Y-%m-%d'), auto_now_add=True)


class Dislike(models.Model):
    dislike_user = models.ForeignKey(StarnaviUser, related_name='dislike_user', on_delete=models.CASCADE)
    dislike_post = models.ForeignKey(Post, related_name='dislike_post', on_delete=models.CASCADE)
    dislike = models.SmallIntegerField(default=0)
    dislike_published = models.DateField(format('%Y-%m-%d'), auto_now_add=True)
