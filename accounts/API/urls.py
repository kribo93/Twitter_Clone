from django.conf.urls import url

from tweets.API.views import (
    TweetListAPIView,
    )

urlpatterns = [

    url(r'^(?P<username>[\w.@+-]+)/tweet/$', TweetListAPIView.as_view(), name='list'),  # /api/tweet/

]
