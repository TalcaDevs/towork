from rest_framework import serializers
from users.models import Request, CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_photo', 'description', 'phone', 'location', 'linkedin', 'portfolio_url']

class RequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Request
        fields = '__all__'