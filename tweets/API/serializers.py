from django.utils.timesince import timesince
from rest_framework import serializers

from accounts.API.serializers import UserDisplaySerializer
from tweets.models import Tweet, TweetMedia


class TweetMediaSerializer(serializers.ModelSerializer):
    media_file = serializers.FileField()
    class Meta:
        model = TweetMedia
        fields = ('media_file',)

class ParentTweetModelSerializer(serializers.ModelSerializer):
    user = UserDisplaySerializer(read_only=True) # write only
    date_display = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    timesince = serializers.SerializerMethodField()
    did_like = serializers.SerializerMethodField()
    media = TweetMediaSerializer(source='tweetmedia_set', many=True, read_only=True)

    class Meta:
        model = Tweet
        fields =[
            'id',
            'user',
            'content',
            'timestamp',
            'date_display',
            'timesince',
            'likes',
            'did_like',
            'media',
        ]

    def get_did_like(self, obj):
        request = self.context.get("request")
        try:
            user = request.user
            if user.is_authenticated():
                if user in obj.liked.all():
                    return True
        except:
            pass
        return False


    def get_likes(self, obj):
        return obj.liked.all().count()

    def get_date_display(self, object):
        return object.timestamp.strftime("%b %d") # ("%b %d %Y at %I:%M %p")

    def get_timesince(self, object):
        return timesince(object.timestamp) + " ago"



class TweetModelSerializer(serializers.ModelSerializer):
    parent_id = serializers.CharField(write_only=True, required=False)
    user = UserDisplaySerializer(read_only=True) # write only
    date_display = serializers.SerializerMethodField()
    timesince = serializers.SerializerMethodField()
    parent = ParentTweetModelSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    did_like = serializers.SerializerMethodField()
    media = TweetMediaSerializer(source='tweetmedia_set', many=True, read_only=True)

    class Meta:
        model = Tweet
        fields = [
            'parent_id',
            'id',
            'user',
            'content',
            'timestamp',
            'date_display',
            'timesince',
            'parent',
            'likes',
            'did_like',
            'reply',
            'media',

        ]
        # read_only_fields = ['reply']

    def create(self, validated_data):
        user = validated_data.get('user')
        media_data = self._context.get('view').request.FILES
        parent_id = validated_data.get('parent_id')
        is_reply = validated_data.get('reply')
        content = validated_data.get('content', 'no-content')
        if len(media_data) < 5:
            tweet = Tweet.objects.create(content=content,
                                         user_id=user.id,
                                         parent_id=parent_id,
                                         reply=is_reply)

            for file in media_data.values():
                TweetMedia.objects.create(media_file=file, tweet=tweet,)
            return tweet
        else:
            print("Upload maximum 4 files")
            raise serializers.ValidationError({'event_type': "Upload maximum 4 files"})

    def get_did_like(self, obj):
        request = self.context.get("request")
        try:
            user = request.user
            if user.is_authenticated():
                if user in obj.liked.all():
                    return True
        except:
            pass
        return False

    def get_likes(self, obj):
        return obj.liked.all().count()

    def get_date_display(self, object):
        return object.timestamp.strftime("%b %d")  # ("%b %d %Y at %I:%M %p")

    def get_timesince(self, object):
        return timesince(object.timestamp) + " ago"
