from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.urls import reverse_lazy
from tweets.models import Tweet
# Create your models here.


class UserProfileManager(models.Manager):
    def all(self):
        qs = self.get_queryset().all()
        """
            With this block we delete the user from "followed by" block if user following of themself
        """
        try:
            if self.instance:
                qs = qs.exclude(user=self.instance)
        except:
            pass
        return qs

    def toggle_follow(self, user, to_toggle_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user)  # return (user_obj, true)
        if to_toggle_user in user_profile.following.all():
            user_profile.following.remove(to_toggle_user)
            added = False
        else:
            user_profile.following.add(to_toggle_user)
            added = True
        return added

    def is_following(self, user, followed_by_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            return False
        if followed_by_user in user_profile.following.all():
            return True
        return False

    def recommended(self, user, limit_to=10):
        profile = user.profile  # my profile
        # following = profile.following.all()  # the profiles of people that i am following
        following = profile.get_following()  # another way
        qs = self.get_queryset().exclude(user__in=following).exclude(id=profile.id).order_by("?")[:limit_to]
        return qs

"""
    Info about 'following' field in 'UserProfile' model:

    user.profile.following --> users I follow
    user.followed_by --> user that follow me (reverse relationship)
"""
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')  #user.profile
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,  related_name='followed_by')
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True, null=True)

    objects = UserProfileManager()  # UserProfile.objects.all()
    # abc = UserProfileManager()  # UserProfile.abc.all()

    def __str__(self):
        return str(self.following.all().count())

    def get_tweets(self):
        user = self.user
        tweets_count = Tweet.objects.filter(user=user)
        return tweets_count

    def get_following(self):
        users = self.following.all()  # User.objects.all()
        return users.exclude(username=self.user.username)

    def get_follow_url(self):
        return reverse_lazy("profiles:follow", kwargs={'username': self.user.username})

    def get_absolute_url(self):
        return reverse_lazy ("profiles:detail", kwargs={'username': self.user.username})

def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    print(instance)
    if created:
        new_profile = UserProfile.objects.get_or_create(user=instance)
        #  if celery + redis
        #  deferred task (email and other)

post_save.connect(post_save_user_receiver, sender=settings.AUTH_USER_MODEL)