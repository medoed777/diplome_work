from rest_framework import serializers

def validate_phone(value):
    if not value.isdigit() or len(value) < 10 or len(value) > 20:
        raise serializers.ValidationError("Номер телефона должен содержать только цифры и быть не менее 10 символов и не более 20.")
    return value
