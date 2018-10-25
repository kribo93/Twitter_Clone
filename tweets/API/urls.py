from django.conf.urls import url
from django.views.generic.base import RedirectView

from tweets.API.views import (
    TweetListAPIView,
    TweetCreateAPIView,
    RetweetAPIView,
    LikeToggleAPIView,
    TweetCreateAPIView,
    TweetDetailView,
    Upload
    )

urlpatterns = [
    url(r'^$', TweetListAPIView.as_view(), name='list'),  # /api/tweet/
    url(r'^create/$', TweetCreateAPIView.as_view(), name='create'),  # /api/tweet/create

    url(r'^upload/$', Upload.as_view({'get': 'list', 'post': 'create'}), name='upload'),


    url(r'^(?P<pk>\d+)/$', TweetDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/like/$', LikeToggleAPIView.as_view(), name='like-toggle'),  # api/tweet/id/like
    url(r'^(?P<pk>\d+)/retweet/$', RetweetAPIView.as_view(), name='retweet'),  # api/tweet/id/retweet
]
