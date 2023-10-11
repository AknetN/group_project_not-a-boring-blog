from rest_framework import serializers
from ..models.repost_request import RepostRequest


class RepostSerializer(serializers.ModelSerializer):
    # because of default there will never be 400 error
    status = serializers.CharField(default="requested")  # Set default value to "requested"

    class Meta:
        model = RepostRequest
        fields = ['requester_id', 'post_id', 'status']

    def create(self, validated_data):
        repost_request = RepostRequest.objects.create(**validated_data)
        return repost_request


class RepostRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepostRequest
        fields = ['id', 'post_id', 'requester_id', 'status', 'created_at']


class UpdateRepostRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepostRequest
        fields = ['status']