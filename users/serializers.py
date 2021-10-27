from rest_framework.exceptions import ValidationError

from users.models import Users
from users.utils import AbstractSerializers
from rest_framework import serializers


class UserRegisterSerializer(AbstractSerializers):
    class Meta:
        model = Users
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'num_tel', 'photo')


class UserChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, label='Старый пароль', style={'input_type': 'password'})
    new_password1 = serializers.CharField(required=True, label='Новый пароль', style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, label='Подтверждение', style={'input_type': 'password'})

    class Meta:
        model = Users
        fields = ('old_password', 'new_password1', 'new_password2')

    def validate_new_password1(self, value):
        if len(value) < 8:
            raise ValidationError('Минимальное число символов 8, у вас %s!' % len(value))
        return value


class ProfileSerializer(AbstractSerializers):
    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'email', 'num_tel')
