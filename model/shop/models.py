from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Shop(models.Model):
    LEVEL_CHOICES = [
        ('A', 'Level A'),
        ('B', 'Level B'),
        ('C', 'Level C'),
        ('D', 'Level D'),
    ]

    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    website = models.CharField(max_length=500, null=True)
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    tags = models.CharField(max_length=255)
    image = models.ImageField(upload_to='shop_images/', null=True, blank=True)
    visited = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='visits')
    visit_time = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=200)

    class Meta:
        unique_together = ('user', 'shop')

    def __str__(self):
        return f"{self.user.username} visited {self.shop.name} on {self.visit_time}"


# class Tag(models.Model):
#     name = models.CharField(max_length=255, unique=True)  # 加unique约束，避免重复标签
#
#     def __str__(self):
#         return self.name
#
#
# class ShopTag(models.Model):
#     shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_tags')
#     tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tagged_shops')
#
#     class Meta:
#         unique_together = ('shop_id', 'tag_id')
#
#     def __str__(self):
#         return f"{self.shop_id} has tag {self.tag_id}"
