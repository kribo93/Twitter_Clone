from rest_framework import generics
from tweets.API.serializers import TweetModelSerializer
from tweets.models import Tweet
from django.db.models import Q
from rest_framework import permissions
from tweets.API.pagination import StandartResultsPagination
from hashtags.models import HashTag
from rest_framework.views import APIView
from rest_framework.response import Response

class TagTweetAPIView(generics.ListAPIView):
    queryset = Tweet.objects.all().order_by("timestamp")
    serializer_class = TweetModelSerializer
    pagination_class = StandartResultsPagination

    def get_serializer_context(self):
        context = super(TagTweetAPIView, self).get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self, *args, **kwargs):
        hashtag = self.kwargs.get("hashtag")
        try:
            hashtag_obj = HashTag.objects.get_or_create(tag=hashtag)[0]
        except:
            pass
        if hashtag_obj:
            qs = hashtag_obj.get_tweets()
            query = self.request.GET.get("q", None)
            if query is not None:
                qs = qs.filter(
                    Q(content__icontains=query) |
                    Q(user__username__icontains=query))
            return qs
        return None