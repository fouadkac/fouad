from rest_framework import serializers
from .models import License

class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ['key', 'owner', 'price', 'active', 'expiry_date']
