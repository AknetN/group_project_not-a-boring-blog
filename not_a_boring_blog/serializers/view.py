from rest_framework import serializers
from ..models.views import View


class ViewSerializer(serializers.Serializer):
    class Meta:
        model = View
        fields = ['post_id', 'user_id', 'timestamp']


class ViewCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = ['view_count']

    def to_representation(self, instance):
        return instance  # Return the dictionary as is
