from rest_framework import serializers
from model.shop.models import Shop
from model.shop.models import Visit
from django.contrib.auth.models import User

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'id',
            'name',
            'country',
            'city',
            'lat',
            'lon',
            'address',
            'phone',
            'email',
            'level',
            'tags',
            'image',
            'visited',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class VisitSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    class Meta:
        model = Visit
        fields = ['id', 'shop_name', 'visit_time', 'notes']

