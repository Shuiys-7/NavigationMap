from rest_framework import serializers
from model.shop.models import Shop
from model.shop.models import Visit
from model.shop.models import Tag
from model.shop.models import ShopTag

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
            'website',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class VisitSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = Visit
        fields = ['id', 'shop_name', 'visit_time', 'notes']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']


class ShopTagSerializer(serializers.ModelSerializer):
    # shop = ShopSerializer()
    # tag = TagSerializer()

    class Meta:
        model = ShopTag
        fields = ['id', 'shop_id', 'tag_id']


