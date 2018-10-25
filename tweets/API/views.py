from rest_framework import generics
from .serializers import TweetModelSerializer
from tweets.models import Tweet, TweetMedia
from django.db.models import Q
from rest_framework import permissions
from .pagination import StandartResultsPagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

class RetweetAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format = None):
        tweet_qs = Tweet.objects.filter(pk=pk)
        message = "Not allowed"
        if tweet_qs.exists() and tweet_qs.count()==1:
            if request.user.is_authenticated():
                new_tweet = Tweet.objects.retweet(request.user, tweet_qs.first())
                if new_tweet is not None:
                    data = TweetModelSerializer(new_tweet).data
                    return Response(data)
                message = "Cannot retweet the same in one day"
        return Response({"message": message}, status=400)

class LikeToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format = None):
        tweet_qs = Tweet.objects.filter(pk=pk)
        likes_count = tweet_qs.values("liked").all().count()
        message = "Not allowed"
        if request.user.is_authenticated:
            is_liked = Tweet.objects.like_toggle(request.user, tweet_qs.first())
            return Response({'liked': is_liked,
                             'likes_count': likes_count})
        return Response({"message": message}, status=400)

class Upload(ModelViewSet):
    serializer_class = TweetModelSerializer
    queryset = Tweet.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        media_data=self.request.FILES)


class TweetCreateAPIView(generics.CreateAPIView):
    serializer_class = TweetModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TweetDetailView(generics.ListAPIView):
    queryset = Tweet.objects.all()
    serializer_class = TweetModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandartResultsPagination

    def get_queryset(self, *args, **kwargs):
        tweet_id = self.kwargs.get("pk")
        qs = Tweet.objects.filter(pk=tweet_id)
        if qs.exists() and qs.count() == 1:
           parent_obj = qs.first()
           qs1 = parent_obj.get_children().filter(reply=True)
           qs = (qs | qs1).distinct().extra(select={"parent_id_null": "parent_id IS NULL"})
        return qs.order_by("-parent_id_null", '-timestamp')

class TweetListAPIView(generics.ListAPIView):
    serializer_class = TweetModelSerializer
    pagination_class = StandartResultsPagination


    def get_serializer_context(self):
        context = super(TweetListAPIView, self).get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self, *args, **kwargs):
        requested_user = self.kwargs.get("username")
        if requested_user:
            qs = Tweet.objects.filter(user__username=requested_user).order_by("-timestamp")
        else:
            im_following = self.request.user.profile.get_following()
            qs1 = Tweet.objects.filter(user__in=im_following)
            qs2 = Tweet.objects.filter(user=self.request.user) # another way to order a tweet is in models.py
            qs = (qs1 | qs2).distinct().order_by("-timestamp")
        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                Q(content__icontains=query) |
                Q(user__username__icontains=query))
        return qs

class SearchTweetAPIView(generics.ListAPIView):
    queryset = Tweet.objects.all().order_by("timestamp")
    serializer_class = TweetModelSerializer
    pagination_class = StandartResultsPagination

    def get_serializer_context(self):
        context = super(SearchTweetAPIView, self).get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self, *args, **kwargs):
        qs = self.queryset
        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                Q(content__icontains=query) |
                Q(user__username__icontains=query))
        return qs
