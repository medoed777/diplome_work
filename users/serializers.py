from rest_framework import serializers


class PhoneSerializers(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class PhoneCodeSerializers(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=4)
