import re

from django.db.models.signals import post_save
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from hashtags.signals import parsed_hashtags
from django.core.validators import FileExtensionValidator
# Create your models here.

class TweetManager(models.Manager):
    def retweet(self, user, parent_obj):
        if parent_obj.parent:
            og_parent = parent_obj.parent
        else:
            og_parent = parent_obj

        qs = self.get_queryset().filter(user=user, parent=og_parent
                                        ).filter(
                                                timestamp__year=timezone.now().year,
                                                timestamp__month=timezone.now().month,
                                                timestamp__day=timezone.now().day,
                                                reply=False,
                                        )
        if qs.exists():
            return None
        obj = self.model(
            parent=og_parent,
            user=user,
            content=parent_obj.content
        )
        obj.save()
        return obj

    def like_toggle(self, user, tweet_obj):
        if user in tweet_obj.liked.all():
            is_liked = False
            tweet_obj.liked.remove(user)
        else:
            is_liked = True
            tweet_obj.liked.add(user)
        return is_liked


class Tweet(models.Model):
    parent = models.ForeignKey("self", blank=True, null=True)  # for retweeting
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.CharField(max_length=140)
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked')
    reply = models.BooleanField(verbose_name="Is a reply?", default=False)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = TweetManager()

    def get_parent(self):
        the_parent = self
        if self.parent:
            the_parent = self.parent
        return the_parent

    def get_children(self):
        parent = self.get_parent()
        qs = Tweet.objects.filter(parent=parent)
        qs_parent = Tweet.objects.filter(pk=parent.pk)
        qs2 = (qs | qs_parent)
        return qs2

    def __str__(self):
        return str(self.content)

    def get_absolute_url(self):
        return reverse("tweet:detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ['-timestamp', 'content']  #another way to do order a tweets in API/views.py

class TweetMedia(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    media_file = models.FileField(upload_to='uploads',
                             validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'bmp',
                                                                                    'gif', 'avi', 'mpeg',
                                                                                    'mp4', 'jpg'])],
                             blank=True,
                             null=True)


def tweet_save_receiver(sender, instance, created, *args, **kwargs):
    if created and not instance.parent:
        # notify a user
        user_regex = r'@(?P<username>[\w.@+-]+)'
        usernames = re.findall(user_regex, instance.content)
        print(usernames)

        # send notification to user
        hash_regex = r'#(?P<hashtag>[\w\d-]+)'
        hashtags = re.findall(hash_regex, instance.content)
        parsed_hashtags.send(sender=instance.__class__, hashtag_list=hashtags)
        # send hashtag signal


post_save.connect(tweet_save_receiver, sender=Tweet)
