import logging
import json
from django.http import HttpRequest

from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from rest_framework import serializers

from .. import models

log = logging.getLogger(__name__)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = "__all__"


class ProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        depth = 1
        fields = "__all__"

class ConversationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ConversationSettings
        fields = "__all__"


class ConversationSettingsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ConversationSettings
        depth = 1
        fields = "__all__"

class ConversationSerializer(serializers.ModelSerializer):
    settings = serializers.SerializerMethodField()
    requests = serializers.SerializerMethodField()

    def get_requests(self, obj):
        request = self.context.get("request")
        sent_requests = models.Request.objects.filter(sender=request.user, receiver= obj.receiver())
        received_requests = models.Request.objects.filter(sender=obj.receiver(), receiver=request.user)
        all_requests = sent_requests | received_requests
        if request and request.user:
            return RequestSerializer(all_requests)
        
    def get_settings(self, obj):
        request = self.context.get("request")
        log.info(request.user)
        if request and request.user:
            return ConversationSettingsSerializer(
                obj.settings.exclude(profile=request.user),
                many=True
            ).data
        return ConversationSettingsSerializer(obj.settings, many=True).data
    class Meta:
        model = models.Conversation
        fields = ["id","name", "room_type", "profiles", "created_at", "message_limit", "settings", "requests"]


class ConversationInfoSerializer(serializers.ModelSerializer):
    settings = serializers.SerializerMethodField()
    requests = serializers.SerializerMethodField()
    
    def get_requests(self, obj):
        request = self.context.get("request")
        other_profile = obj.profiles.exclude(id=request.user.id).first()

        sent_requests = models.Request.objects.filter(sender = request.user, receiver = other_profile)
        received_requests = models.Request.objects.filter(sender = other_profile, receiver = request.user)
        all_requests = sent_requests | received_requests
        if request and request.user:
            return RequestSerializer(all_requests, many=True).data
        
    def get_settings(self, obj):
        request = self.context.get("request")
        log.info(request.user)

        if request and request.user:
            return ConversationSettingsInfoSerializer(
                obj.settings.exclude(profile=request.user),  # Filter settings here
                many=True
            ).data
        return ConversationSettingsInfoSerializer(obj.settings, many=True).data
    
    class Meta:
        model = models.Conversation
        depth = 1
        fields = ["id","name", "room_type", "profiles", "created_at", "message_limit", "settings", "requests"]

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Follower
        fields = "__all__"


class FollowerInfoSerializer(serializers.ModelSerializer):
    follower = ProfileInfoSerializer()
    following = ProfileInfoSerializer()
    class Meta:
        model = models.Follower
        depth = 1
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer()
    conversation = ConversationSerializer()
    class Meta:
        model = models.Message
        fields = "__all__"


class MessageInfoSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer()
    conversation = ConversationSerializer()
    class Meta:
        model = models.Message
        depth = 1
        fields = "__all__"

class RequestSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer()
    receiver = ProfileSerializer()
    class Meta:
        depth = 1
        model = models.Request
        fields = "__all__"


class RequestInfoSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer(read_only=True)
    receiver = ProfileSerializer(read_only=True)
    class Meta:
        model = models.Request
        depth = 1
        fields = "__all__"