from  django.contrib.auth import get_user_model
from rest_framework import serializers
from django.urls import reverse_lazy
from accounts.models import UserProfile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    photo = serializers.FileField()
    class Meta:
        model = UserProfile
        fields = ('photo',)


class UserDisplaySerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    photo = ProfileSerializer(source='profile', many=False, read_only=True)
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'follower_count',
            'url',
            'photo',
        ]

    def get_follower_count(self, obj):
        return 0

    def get_url(self, obj):
        return reverse_lazy("profiles:detail", kwargs={'username': obj.username})
