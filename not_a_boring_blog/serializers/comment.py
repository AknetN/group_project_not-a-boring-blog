from rest_framework import serializers
from ..models.comment import Comment


class ReplyCommentSerializer(serializers.ModelSerializer):
    '''Serializer for reply'''
    body = serializers.CharField(max_length=500, required=True)
    author_username = serializers.SerializerMethodField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%B-%Y %H:%M", required=False)
    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'author_username', 'created_at']

    def update(self, instance, validated_data):
        # Add custom logic here, if needed
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance

    def get_author_username(self, obj):
        return obj.author.username


class ReplyDetailsSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%B-%Y %H:%M", required=False)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_username', 'body', 'created_at', 'parent_id']

    def get_author_username(self, obj):
        return obj.author.username


class CommentSerializer(serializers.ModelSerializer):
    replies = ReplyDetailsSerializer(many=True)
    author_username = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%B-%Y %H:%M", required=False)
    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'author_username', 'body', 'created_at', 'author', 'replies']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['replies_count'] = instance.replies.count()
        return representation

    def get_author_username(self, obj):
        return obj.author.username
