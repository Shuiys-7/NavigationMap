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

    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    tags = models.CharField(max_length=200)
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
