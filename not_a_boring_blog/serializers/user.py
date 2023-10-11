from rest_framework import serializers
from ..models.user import Role
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class RoleSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(max_length=255, allow_blank=True, required=False)

    class Meta:
        model = Role
        fields = ['is_moderator', 'is_blogger', 'is_admin', 'bio']

    def validate(self, data):
        is_moderator = data.get('is_moderator', False)
        is_blogger = data.get('is_blogger', False)
        is_admin = data.get('is_admin', False)
        # Ensure that only one of the three boolean values is True
        if sum([is_moderator, is_blogger, is_admin]) != 1:
            raise serializers.ValidationError("Only one attribute can be True at a time!")
        return data


class BioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['bio']


class UserListSerializer(serializers.ModelSerializer):
    role = BioSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    # role = RoleSerializer(default={'is_blogger': True})  # Embed the RoleSerializer
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_style': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        role_data = {'is_blogger': True}  # Extract role data
        user = User.objects.create(
            username=validated_data['username'].lower(),
            email=validated_data['email'].lower(),
            password=make_password(validated_data['password'])
        )
        Role.objects.create(user=user, **role_data)  # Create a Role instance associated with the user
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateUserBioSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(max_length=500, allow_blank=True, required=False, default="")

    class Meta:
        model = Role
        fields = ['bio']


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        # Check if the new password and confirmation match
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("New password and confirmation do not match.")
        return data


class LoginUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, allow_blank=True, required=False)
    email = serializers.CharField(max_length=255, allow_blank=True, required=False)
    password = serializers.CharField(required=True)
    role = RoleSerializer(required=False, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']


class UpdateRoleSerializer(serializers.ModelSerializer):
    '''Serializes role updating'''
    role = RoleSerializer(default={
        'is_blogger': True,
        'is_moderator': False,
        'is_admin': False
    })

    class Meta:
        model = User
        fields = ['role']

    def update(self, instance, validated_data):
        role_data = validated_data.pop('role', {})  # Extract role data
        role_instance, created = Role.objects.get_or_create(user=instance, defaults={'is_blogger': True})

        # Update role fields
        role_instance.is_moderator = role_data.get('is_moderator', role_instance.is_moderator)
        role_instance.is_blogger = role_data.get('is_blogger', role_instance.is_blogger)
        role_instance.is_admin = role_data.get('is_admin', role_instance.is_admin)
        instance.save()
        role_instance.save()
        return instance