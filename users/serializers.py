from users.models import Users
from users.utils import AbstractSerializers
from rest_framework import serializers


class UserSerializer(AbstractSerializers):
    class Meta:
        model = Users
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'num_tel', 'photo')


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, label='Старый пароль', style={'input_type': 'password'})
    new_password1 = serializers.CharField(required=True, label='Новый пароль', style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, label='Подтверждение', style={'input_type': 'password'})


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'email', 'num_tel')
