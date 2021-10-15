from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import re


class AbstractSerializers(serializers.ModelSerializer):
    """Класс валидации полей"""

    def validate_first_name(self, value):
        check = re.findall(r'\d|\W', value)
        if check:
            raise ValidationError('Имя должно содержать только буквы')
        if len(value) > 20:
            raise ValidationError('Максимальное число символов 20, у вас %s' % len(value))
        if len(value) < 3 and value:
            raise ValidationError('Минимальное число символов 3, у вас %s' % len(value))
        return value

    def validate_last_name(self, value):
        check = re.findall(r'\d|\W', value)
        if check:
            raise ValidationError('Фамилия должна содержать только буквы')
        if len(value) > 25:
            raise ValidationError('Максимальное число символов 25, у вас %s' % len(value))
        if len(value) < 3 and value:
            raise ValidationError('Минимальное число символов 3, у вас %s' % len(value))
        return value

    def validate_num_tel(self, value):
        check = re.findall(r'\D', value)
        if check:
            raise ValidationError('Номер должен содержать только цифры!')
        if len(value) < 12 and value:
            raise ValidationError('Минимальное число символов 12, у вас %s' % len(value))
        if len(value) > 20 and value:
            raise ValidationError('Максимальное число символов 20, у вас %s' % len(value))
        return value

    def validate_email(self, value):
        if len(value) <= 11:
            raise ValidationError('Email должен содержать более 3 символов перед @!')
        return value
