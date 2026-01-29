from rest_framework import serializers
from .models import Skill, Profile
from django.contrib.auth.models import User
from .models import ConnectionRequest

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    skills_known = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all()
    )
    skills_wanted = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all()
    )

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'location', 'skills_known', 'skills_wanted']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']        

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user        

class ConnectionRequestSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)  # show sender username
    receiver = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at', "sender_username", "receiver_username"]