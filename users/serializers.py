from rest_framework import serializers

from users.models import User, PhoneCode, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone']


class PhoneSerializers(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

    class Meta:
        model = PhoneCode
        fields = ['phone', 'code', 'created_at']


class PhoneCodeSerializers(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=4)

    class Meta:
        model = Profile
        fields = ['user', 'invaite_code']
