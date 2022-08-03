from rest_framework import serializers
from manager import models

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Package
        fields = ('id','name')

class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pricing
        fields = ('id','name')

class SubscriptionSerializer(serializers.ModelSerializer):
    package_id = PackageSerializer(read_only=True)
    pricing = PricingSerializer(read_only=True)
    class Meta:
        model = models.Subscription
        fields = ['id', 'package_id', 'pricing']